# ChatGPT Bridge System

本系统允许你通过一个轻量级的 HTML 客户端 (`client_a.html`) 在任意设备上远程控制并使用运行在另一台电脑 (`Server B`) 上的 ChatGPT 网页版。

## ✨ 主要功能 (Features)

*   **远程对话**: 在内网任意设备上通过网页与 ChatGPT 对话。
*   **实时流式响应**: 打字机效果同步显示。
*   **新建对话**: 支持快捷键 (`Ctrl+Shift+O`) 或点击按钮一键开启新会话（自动处理侧边栏）。
*   **历史记录**: 查看和切换最近的对话历史 (由 Server B 自动获取)。
*   **现代化 UI**:
    *   **侧边栏管理**: 支持展开/收起，手机端适配。
    *   **现代化主题**: 支持浅色/深色模式切换。
*   **可视化服务端**: 提供 GUI 界面管理服务启动、停止及日志查看。

## 🛠️ 环境准备 (Server B)

服务端运行在已登录 ChatGPT 的电脑上（推荐 Windows）。

1.  **安装 Python 3.9+**。
2.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **安装 Playwright 浏览器内核**:
    ```bash
    playwright install chromium
    ```

## 🚀 快速启动 (推荐：GUI 模式)

### 1. 启动 Chrome 浏览器
你需要先启动一个开启了远程调试端口 (`9222`) 的 Chrome 浏览器，并**登录 ChatGPT**。
*   **方式 A (推荐)**: 直接双击运行项目目录下的 `start_chrome_clone.bat` (会自动创建一个独立的 Chrome 环境，互不干扰)。
*   **方式 B (手动)**: 命令行运行 `"chrome.exe路径" --remote-debugging-port=9222`。

### 2. 启动服务端
双击运行 `server_gui.py` (或在命令行输入 `python server_gui.py`)。
*   **配置**: 确认端口为 `2222`，Token 默认为 `123456`。
*   点击 **“启动服务器 (Start)”**。
*   观察状态栏变为绿色 "运行中"，且日志显示 "成功接管 Chrome"。
*   在弹出的Chrome页面手动登录GPT账户

### 3. 连接客户端
1.  将 `client_a.html` 发送到同一局域网下的任意电脑或手机。
2.  直接用浏览器打开 `client_a.html`。
3.  在弹出的配置窗口中：
    *   **IP 地址**: 输入 Server B 电脑的局域网 IP (如 `192.168.1.5`)。
    *   **端口**: 默认 `2222`。
    *   **Auth_Token**: 默认 `123456`。
4.  点击 **“保存并连接”**。

## ⌨️ 操作指南

*   **发送消息**: 在底部输入框输入文字，回车发送 (Shift+Enter 换行)。
*   **新建对话**: 点击左上角 `+ 新建对话` 按钮。
*   **切换历史**: 展开左侧侧边栏，点击历史记录标题切换会话。
*   **关闭/打开侧边栏**: 顶部导航栏左侧按钮 (移动端会自动收起)。

## 🔧 常见问题 (Troubleshooting)

1.  **连接不上 (Connection Failed)**
    *   检查 Server B 防火墙是否放行了 `2222` 端口。
    *   确保两台设备在同一 Wi-Fi/局域网下。
    *   检查 Client A 配置的 IP 是否正确。

2.  **新建对话没反应**
    *   服务端会自动尝试 `Ctrl+Shift+O` 快捷键。如果无效，会尝试点击页面按钮。
    *   请确保 Server B 的浏览器窗口**没有被最小化**（可以被遮挡，但不能最小化到任务栏），否则 Playwright 可能无法点击元素。

3.  **任务栏闪烁**
    *   最新版已移除强制置顶逻辑，操作应为后台静默进行。

4.  **回复慢**
    *   信息多次传输会有一定延迟，Server B 电脑的网络环境可能会影响速度。
    *   Server B 模拟输入设置了一定延迟，以模拟人类打字速度。

## 📂 项目结构
*   `server_gui.py`: 服务端控制面板 (GUI)。
*   `server_b.py`: 服务端核心逻辑 (WebSocket + Playwright)。
*   `client_a.html`: 客户端前端页面。
*   `start_chrome_clone.bat`: 辅助脚本，用于启动独立环境的 Chrome。



