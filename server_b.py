import os
import asyncio
import uvicorn
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from playwright.async_api import async_playwright, Page, BrowserContext, Browser

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 环境变量获取配置
import os
import asyncio
import uvicorn
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from playwright.async_api import async_playwright, Page, BrowserContext, Browser

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 环境变量获取配置
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "123456")
PORT = int(os.getenv("PORT", "2222"))
HOST = "0.0.0.0"
CHROME_DEBUG_URL = "http://127.0.0.1:9222" # Chrome 调试端口地址

app = FastAPI()

# 全局变量存储 Playwright 对象
playwright_instance = None
browser_context: BrowserContext = None
page: Page = None

@app.on_event("startup")
async def startup_event():
    """服务启动时初始化 Playwright 和 浏览器"""
    global playwright_instance, browser_context, page
    logger.info("正在启动服务...")
    
    playwright_instance = await async_playwright().start()
    
    try:
        # 尝试连接已打开的 Chrome (需要以 --remote-debugging-port=9222 启动)
        logger.info(f"尝试连接已运行的 Chrome ({CHROME_DEBUG_URL})...")
        try:
            browser_context = await playwright_instance.chromium.connect_over_cdp(CHROME_DEBUG_URL)
            logger.info("成功接管已运行的 Chrome 浏览器！")
            
            # 获取现有页面或新建页面
            if browser_context.contexts[0].pages:
                page = browser_context.contexts[0].pages[0]
                logger.info("复用当前活动标签页")
            else:
                page = await browser_context.new_page()
                logger.info("创建新标签页")

        except Exception as cdp_error:
            logger.warning(f"无法连接到现有 Chrome: {cdp_error}")
            logger.info(">>> 若要实现“直接操作Chrome”，请确保 Chrome 已完全关闭，然后使用以下命令启动：")
            logger.info(">>> chrome.exe --remote-debugging-port=9222 --user-data-dir=\"C:\\selenium\\ChromeProfile\"")
            logger.info(">>> (注意：--user-data-dir 必须指定一个非默认的用户目录，否则可能与当前打开的 Chrome 冲突)")
            logger.info("正在回退到独立浏览器模式...")
            
            # 回退：启动一个新的持久化上下文
            user_data_dir = "./playwright_data"
            browser_context = await playwright_instance.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                viewport={"width": 1280, "height": 720},
                channel="chrome", # 尝试使用本机安装的 Chrome
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()

        # 无论哪种方式，都尝试导航一下（或者检查当前网址）
        current_url = page.url
        if "chatgpt.com" not in current_url:
            logger.info("正在导航至 https://chatgpt.com ...")
            await page.goto("https://chatgpt.com", timeout=60000)
        else:
            logger.info("当前页面已在 ChatGPT")

        logger.info("浏览器就绪。")
        
    except Exception as e:
        logger.error(f"启动/连接浏览器失败: {e}")
        # 这里不 raise，允许服务启动，但在处理请求时会报错
        
@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭时清理资源"""
    logger.info("正在关闭资源...")
    # 注意：如果是 connect_over_cdp，close() 可能会关闭浏览器，也可能只是断开连接，视具体实现而定
    # 通常 disconnect() 是断开 CDP，close() 关闭 Context
    if browser_context:
        try:
            await browser_context.close()
        except:
            pass
    if playwright_instance:
        await playwright_instance.stop()

async def get_latest_assistant_response_locator():
    """获取最后一个助手回复的消息块"""
    return page.locator("div[data-message-author-role='assistant']").last

async def is_generating():
    """检查是否正在生成（通过'停止生成'按钮存在判断）"""
    try:
        stop_btn = page.locator("button[aria-label='Stop generating']")
        return await stop_btn.is_visible()
    except:
        return False

async def get_or_create_page():
    """动态获取一个可用的 ChatGPT 页面，如果不存在则创建"""
    global browser_context, page
    
    # 1. 如果全局 page 看起来可用，先检查一下
    if page and not page.is_closed():
        try:
            if "chatgpt.com" in page.url:
                return page
        except:
            pass
            
    # 2. 遍历所有 Context 找页面
    if browser_context:
        for ctx in browser_context.contexts if hasattr(browser_context, 'contexts') else [browser_context]:
             for p in ctx.pages:
                 try:
                     if "chatgpt.com" in p.url:
                         page = p
                         return page
                 except:
                     pass
                     
    # 3. 如果没找到，但在 Context 里有任何页面，就复用第一个并跳转
    if browser_context:
        # 再次遍历获取第一个可用页面
        all_pages = []
        if hasattr(browser_context, 'contexts'):
            for ctx in browser_context.contexts:
                all_pages.extend(ctx.pages)
        else:
            all_pages = browser_context.pages
            
        if all_pages:
            page = all_pages[0]
            try:
                await page.goto("https://chatgpt.com")
                return page
            except:
                pass
    
    # 4. 实在没有，新建一个
    if browser_context:
        try:
            page = await browser_context.new_page()
            await page.goto("https://chatgpt.com")
            return page
        except Exception as e:
            logger.error(f"创建新页面失败: {e}")
            raise e
            
    raise Exception("浏览器未初始化，无法获取页面")

@app.get("/ping")
async def ping():
    """健康检查接口"""
    return {"status": "ok", "browser_connected": page is not None}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    client_token = websocket.query_params.get("token")
    if client_token != AUTH_TOKEN:
        await websocket.send_json({"type": "error", "message": "鉴权失败"})
        await websocket.close()
        return

    logger.info(f"客户端已连接: {websocket.client}")

    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")

            logger.info(f"DEBUG: 收到指令: {message_type}")

            if message_type == "ping":
                # 添加 ping/pong 处理
                await websocket.send_json({"type": "pong"})
                continue

            if message_type == "chat":
                if not page:
                    await websocket.send_json({"type": "error", "message": "服务端浏览器未就绪"})
                    continue

                user_message = data.get("message", "")
                logger.info(f"收到消息: {user_message[:20]}...")

                if not user_message:
                    continue

                try:
                    # 1. 定位输入框
                    input_box = page.locator("textarea[id='prompt-textarea']")
                    if not await input_box.is_visible():
                        input_box = page.locator("div[contenteditable='true']")
                    
                    if not await input_box.is_visible():
                         raise Exception("无法找到输入框，请手动确保浏览器处于 ChatGPT 聊天界面")

                    # 2. 聚焦并输入
                    await input_box.fill("") 
                    await input_box.fill(user_message)
                    
                    # 3. 发送
                    send_btn = page.locator("button[data-testid='send-button']")
                    if await send_btn.is_visible():
                        await send_btn.click()
                    else:
                        await input_box.press("Enter")
                    
                    # 4. 监听流式回复
                    await asyncio.sleep(1) 

                    previous_text = ""
                    last_response = await get_latest_assistant_response_locator()
                    no_change_count = 0
                    
                    while True:
                        generating = await is_generating()
                        current_text = await last_response.inner_text()
                        
                        if len(current_text) > len(previous_text):
                            delta = current_text[len(previous_text):]
                            await websocket.send_json({"type": "delta", "content": delta})
                            previous_text = current_text
                            no_change_count = 0
                        else:
                            no_change_count += 1
                        
                        if not generating and len(current_text) > 0 and no_change_count > 5:
                            break
                        if len(current_text) == 0 and generating:
                            no_change_count = 0

                        await asyncio.sleep(0.5)

                    await websocket.send_json({"type": "done"})

                except Exception as e:
                    logger.error(f"处理消息异常: {e}")
                    if "browser_context" in str(e) or "Target page" in str(e):
                        err_msg = "浏览器连接已断开，正在尝试重连..."
                        await websocket.send_json({"type": "error", "message": err_msg})
                    else:
                        await websocket.send_json({"type": "error", "message": str(e)})
            
            elif message_type == "get_history":
                try:
                    active_page = await get_or_create_page()
                    chats = await get_sidebar_chats(active_page)
                    await websocket.send_json({"type": "history_list", "data": chats})
                except Exception as e:
                    logger.error(f"获取历史记录失败: {e}")
                    await websocket.send_json({"type": "error", "message": f"获取历史失败: {str(e)}"})

            elif message_type == "switch_chat":
                url_suffix = data.get("url")
                if url_suffix:
                    try:
                        active_page = await get_or_create_page()
                        target_url = "https://chatgpt.com" + url_suffix
                        logger.info(f"切换会话: {target_url}")
                        await active_page.goto(target_url)
                        # 切换后自动获取最新的几条消息
                        await asyncio.sleep(2) # 等待加载
                        msgs = await get_chat_messages(active_page, limit=6, offset=0)
                        await websocket.send_json({"type": "message_history", "data": msgs, "has_more": True})
                    except Exception as e:
                        logger.error(f"切换会话失败: {e}")
                        await websocket.send_json({"type": "error", "message": str(e)})

            elif message_type == "get_messages":
                limit = data.get("limit", 10)
                offset = data.get("offset", 0)
                try:
                    active_page = await get_or_create_page()
                    msgs = await get_chat_messages(active_page, limit=limit, offset=offset)
                    await websocket.send_json({"type": "message_history", "data": msgs, "has_more": True}) # 简化处理，总是假设有更多
                except Exception as e:
                    logger.error(f"获取消息历史失败: {e}")
                    await websocket.send_json({"type": "error", "message": str(e)})

            elif message_type == "new_chat":
                try:
                    active_page = await get_or_create_page()
                    logger.info("执行新建对话逻辑...")
                    
                    found_and_clicked = False

                    # 0. 优先尝试快捷键 (根据用户提供的 HTML 发现支持 Ctrl+Shift+O)
                    try:
                        logger.info("尝试使用快捷键 Ctrl+Shift+O ...")
                        # 去掉了 bring_to_front 以避免任务栏闪烁
                        await active_page.keyboard.press("Control+Shift+O")
                        await asyncio.sleep(1) # 等待响应
                        # 这里很难判断快捷键是否生效，所以我们继续执行点击逻辑作为保障，
                        # 或者如果跳转了页面，下面的 locator 可能会报错或失效，这是预期的。
                    except Exception as e:
                        logger.warning(f"快捷键触发失败: {e}")
                    
                    # 定义两个关键元素 (确认 selector 与用户提供的一致)
                    new_chat_selector = "a[data-testid='create-new-chat-button']"
                    sidebar_toggle_selector = "button[data-testid='open-sidebar-button']"
                    
                    new_chat_btn = active_page.locator(new_chat_selector).first
                    
                    # 1. 第一次尝试寻找并点击"新建对话"
                    if await new_chat_btn.is_visible():
                        logger.info("找到新建对话按钮，尝试 Hover 后点击")
                        try:
                            await new_chat_btn.hover()
                            await asyncio.sleep(0.5) 
                            await new_chat_btn.click(force=True)
                            found_and_clicked = True
                        except Exception as e:
                             logger.warning(f"直接点击失败: {e}")

                    if not found_and_clicked:
                        logger.info("未成功点击新建按钮，尝试寻找展开侧边栏按钮...")
                        # 2. 尝试寻找"展开侧边栏"
                        toggle_btn = active_page.locator(sidebar_toggle_selector).first
                        
                        if await toggle_btn.is_visible():
                            logger.info("找到侧边栏展开按钮，尝试 Hover 后点击...")
                            try:
                                await toggle_btn.hover()
                                await asyncio.sleep(0.5)
                                await toggle_btn.click(force=True)
                                
                                # 稍作等待，侧边栏动画
                                await asyncio.sleep(1.0)
                                
                                # 3. 展开后再次尝试寻找"新建对话"
                                if await new_chat_btn.is_visible():
                                    logger.info("侧边栏展开后，找到新建对话按钮，Hover 后点击")
                                    await new_chat_btn.hover()
                                    await asyncio.sleep(0.5)
                                    await new_chat_btn.click(force=True)
                                    found_and_clicked = True
                                else:
                                    logger.warning("侧边栏展开后，仍未找到新建对话按钮")
                            except Exception as e:
                                logger.warning(f"操作侧边栏按钮失败: {e}")
                        else:
                            logger.warning("未找到侧边栏展开按钮")

                    # 4. 兜底方案：如果上面都没成功，直接跳 URL
                    if not found_and_clicked:
                        logger.warning("UI 操作失败，执行强制 URL 跳转兜底")
                        await active_page.goto("https://chatgpt.com/")
                    
                    # 等待页面可能的刷新
                    await asyncio.sleep(1)
                    await websocket.send_json({"type": "new_chat_success"})

                except Exception as e:
                    logger.error(f"新建对话失败: {e}")
                    await websocket.send_json({"type": "error", "message": f"新建对话失败: {str(e)}"})

    except WebSocketDisconnect:
        logger.info("客户端断开连接")
    except Exception as e:
        logger.error(f"WebSocket 异常: {e}")

async def get_sidebar_chats(page_obj):
    """获取侧边栏聊天列表，如果侧边栏隐藏则自动展开"""
    # 1. 尝试查找链接
    # 注意：ChatGPT 侧边栏结构经常变，这里假设是 nav 里的 a 标签
    # 也可以用 data-testid="conversations-list" (不一定有)
    
    # 辅助函数：提取
    async def extract_links():
        # 选择器根据用户提供的截图特征：a[href^='/c/'] 且包含 div
        # 排除掉 "New Chat" 链接 (通常是 /)
        links = page_obj.locator("nav a[href^='/c/']")
        count = await links.count()
        results = []
        for i in range(count):
            try:
                # 限制只取前 20 个，防止太多
                if i > 20: break
                item = links.nth(i)
                # 获取标题 (通常在 div.truncate 或 div.relative 中)
                title = await item.inner_text()
                href = await item.get_attribute("href")
                # 简单清理标题换行
                title = title.replace("\n", " ").strip()
                if href and href not in [r['id'] for r in results]:
                    results.append({"id": href, "title": title or "无标题会话"})
            except:
                pass
        return results

    chats = await extract_links()
    
    # 2. 如果没找到，并且存在“展开侧边栏”按钮，则点击它
    if not chats:
        try:
            # 用户指定的 [data-testid="open-sidebar-button"]
            toggle_btn = page_obj.locator("button[data-testid='open-sidebar-button']")
            if await toggle_btn.is_visible():
                logger.info("侧边栏未显示，尝试点击展开按钮...")
                await toggle_btn.click()
                await asyncio.sleep(1) # 等动画
                chats = await extract_links()
        except Exception as e:
            logger.warning(f"尝试展开侧边栏失败: {e}")
            
    return chats

async def get_chat_messages(page_obj, limit=6, offset=0):
    """获取聊天消息历史"""
    # 定位消息容器
    # role='user' 或 role='assistant'
    msg_locators = page_obj.locator("div[data-message-author-role]")
    total_count = await msg_locators.count()
    
    if total_count == 0:
        return []

    # 计算切片索引 (倒序)
    # 例如 total=100, limit=6, offset=0 -> 取 [94, 100]
    # offset=6 -> 取 [88, 94]
    
    end_index = total_count - offset
    start_index = max(0, end_index - limit)
    
    if end_index <= 0:
        return []

    results = []
    # Playwright 的 nth 是 0-based
    for i in range(start_index, end_index):
        try:
            msg_item = msg_locators.nth(i)
            role = await msg_item.get_attribute("data-message-author-role")
            text = await msg_item.inner_text()
            results.append({
                "role": role,
                "content": text
            })
        except:
            continue
            
    return results


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
