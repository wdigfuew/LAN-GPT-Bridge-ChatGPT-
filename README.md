# ChatGPT Bridge System (双端内网穿透系统)

本系统允许你通过一个轻量级的 HTML 客户端 (`client_a.html`) 在任意设备上远程控制并使用运行在另一台电脑 (`Server B`) 上的 ChatGPT 网页版。
此项目涉嫌

## ✨ 主要功能 (Features)

*   **远程对话**: 在内网任意设备上通过网页与 ChatGPT 对话。
*   **实时流式响应**: 打字机效果同步显示。
*   **新建对话**: 支持快捷键 (`Ctrl+Shift+O`) 或点击按钮一键开启新会话（自动处理侧边栏）。
*   **历史记录**: 查看和切换最近的对话历史 (由 Server B 自动获取)。
*   **现代化 UI**:
    *   **侧边栏管理**: 支持展开/收起，手机端适配。
    *   **现代化主题**: 支持浅色/深色模式切换。
*   **可视化服务端**: 提供 GUI 界面管理服务启动、停止及日志查看。
*   **新增**:2026-1-17：已支持表格，公式，Markdown，Canvas显示。

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
*   **配置**: 确认端口为 `2222`，Token 默认为 `123456` (环境变量可配)。
*   点击 **“启动服务器 (Start)”**。
*   观察状态栏变为绿色 "运行中"，且日志显示 "成功接管 Chrome"。

### 3. 连接客户端 (两种方式)

**方式 A: Web 远程访问 (推荐)**
无需传输文件，直接在另一台设备 (手机/平板/电脑) 的浏览器中输入 Server B 的 IP 和端口。
*   例如: `http://192.168.1.5:2222`
*   系统会自动识别 IP 并连接，无需手动配置。
*   Token: 需手动输入 (默认 123456)。

**方式 B: 离线文件模式**
1.  将 `client_a.html` 发送到客户端设备。
2.  用浏览器打开该文件。
3.  在配置窗口中：
    *   **IP 地址**: 输入 Server B 电脑的局域网 IP (如 `192.168.1.5`)。
    *   **端口**: 默认 `2222`。
    *   **Token**: 需手动输入 (默认 `123456`)。
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

本项目仅供学习、研究和技术交流用途。
作者不保证本项目的正确性、完整性或适用性。使用本项目所产生的一切后果，包括但不限于账号封禁、数据丢失、服务中断、法律风险或其他损失，均由使用者自行承担。
本项目不鼓励、支持或纵容任何违反法律法规或第三方平台服务条款的行为。使用者有责任在使用本项目前，确认其行为符合所在地法律法规以及相关平台或服务的使用政策。
作者不对任何因使用、修改、分发或依赖本项目而产生的直接或间接损失承担责任。

This project is provided for educational, research, and technical exchange purposes only.

The author makes no warranties regarding the correctness, completeness, or suitability of this project. Any consequences arising from the use of this project, including but not limited to account suspension, data loss, service interruption, legal issues, or other damages, are solely the responsibility of the user.

This project does not encourage, support, or endorse any activities that violate applicable laws, regulations, or third-party terms of service. Users are responsible for ensuring that their use of this project complies with all relevant laws and platform policies.

The author shall not be held liable for any direct or indirect damages resulting from the use, modification, distribution, or reliance on this project.


