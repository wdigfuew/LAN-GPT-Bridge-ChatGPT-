@echo off
chcp 65001 >nul
echo ========================================================
echo       Chrome 调试模式 (复制配置版)
echo ========================================================
echo.
echo 由于您的默认浏览器配置可能被占用或受保护，
echo 本脚本将尝试【复制】您的登录状态到一个临时目录来启动。
echo.

set "SRC_PROFILE=%LOCALAPPDATA%\Google\Chrome\User Data"
set "DST_PROFILE=%cd%\chrome_bridge_profile"

echo [1/3] 正在检查配置...
if not exist "%SRC_PROFILE%" (
    echo [错误] 找不到默认的 Chrome 用户数据目录。
    pause
    exit
)

:: 为了速度，我们只复制关键的 Cookie 和 Login Data，不复制缓存
echo [2/3] 正在克隆用户数据到: %DST_PROFILE%
echo        这可能需要几秒钟...

if not exist "%DST_PROFILE%" mkdir "%DST_PROFILE%"
if not exist "%DST_PROFILE%\Default" mkdir "%DST_PROFILE%\Default"

:: 复制核心认证文件
copy "%SRC_PROFILE%\Last Version" "%DST_PROFILE%\" >nul 2>&1
copy "%SRC_PROFILE%\Local State" "%DST_PROFILE%\" >nul 2>&1
robocopy "%SRC_PROFILE%\Default" "%DST_PROFILE%\Default" Cookies Login* Web* Preferences /xc /xn /xo >nul 2>&1

echo 配置克隆完成。
echo.

echo [3/3] 正在启动独立 Chrome...
set "CHROME_PATH="
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" set "CHROME_PATH=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"

:: 启动，指定新的 user-data-dir
start "" "%CHROME_PATH%" --remote-debugging-port=9222 --user-data-dir="%DST_PROFILE%" --remote-allow-origins=* https://chatgpt.com

echo 正在检查端口...
:wait_loop
timeout /t 2 /nobreak >nul
netstat -an | find "9222" | find "LISTENING" >nul
if %errorlevel% equ 0 (
    echo.
    echo ✅ 成功！端口 9222 已开启。
    echo 注意：这使用了一个【克隆】的配置，如果您发现没登录，
    echo 请在这个新窗口里手动登录一次（只需一次，后续会保留在 chrome_bridge_profile 中）。
    echo.
    echo 现在运行 python server_b.py
    echo.
    pause
    exit
) else (
    echo ...等待中...
    goto wait_loop
)
