import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import sys
import threading
import os
import queue
import re

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatGPT Bridge Server Control")
        self.root.geometry("600x550")
        
        # 默认配置
        self.default_port = "2222"
        self.default_token = "123456"
        self.process = None
        self.is_running = False
        
        # 布局
        self.create_widgets()
        
        # 日志队列
        self.log_queue = queue.Queue()
        self.root.after(100, self.process_log_queue)

    def create_widgets(self):
        # 1. 配置区域
        config_frame = ttk.LabelFrame(self.root, text=" 配置 (Configuration) ", padding=(10, 5))
        config_frame.pack(fill="x", padx=10, pady=5)
        
        # 端口
        ttk.Label(config_frame, text="端口 (Port):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.port_var = tk.StringVar(value=self.default_port)
        ttk.Entry(config_frame, textvariable=self.port_var, width=10).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Token
        ttk.Label(config_frame, text="Token:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.token_var = tk.StringVar(value=self.default_token)
        ttk.Entry(config_frame, textvariable=self.token_var, width=15).grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # 2. 浏览器区域
        browser_frame = ttk.LabelFrame(self.root, text=" 浏览器控制 (Browser) ", padding=(10, 5))
        browser_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(browser_frame, text="启动克隆版 Chrome (备用)", command=self.launch_chrome_clone).pack(side="left", padx=5)
        ttk.Label(browser_frame, text="← 请先启动浏览器并登录 ChatGPT").pack(side="left", padx=5)

        # 3. 状态与连接显示
        status_frame = ttk.Frame(self.root, padding=(10, 5))
        status_frame.pack(fill="x", padx=10)
        
        self.status_label = ttk.Label(status_frame, text="状态: 已停止", foreground="red", font=("Microsoft YaHei", 10, "bold"))
        self.status_label.pack(side="left")
        
        self.client_label = ttk.Label(status_frame, text="客户端: 无连接", foreground="gray")
        self.client_label.pack(side="right")

        # 4. 日志区域
        log_frame = ttk.LabelFrame(self.root, text=" 运行日志 (Logs) ", padding=(5, 5))
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, state='disabled', height=10, font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True)
        # 配置 Tag 颜色
        self.log_text.tag_config("INFO", foreground="black")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("CLIENT", foreground="blue")

        # 5. 底部控制按钮
        btn_frame = ttk.Frame(self.root, padding=(10, 10))
        btn_frame.pack(fill="x")
        
        self.start_btn = ttk.Button(btn_frame, text="启动服务器 (Start)", command=self.toggle_server)
        self.start_btn.pack(side="left", expand=True, fill="x", padx=5)
        
        ttk.Button(btn_frame, text="退出 (Exit)", command=self.on_close).pack(side="right", padx=5)

    def log(self, message, level="INFO"):
        self.log_queue.put((message, level))

    def process_log_queue(self):
        while not self.log_queue.empty():
            msg, level = self.log_queue.get()
            self.log_text.configure(state='normal')
            self.log_text.insert(tk.END, msg + "\n", level)
            self.log_text.see(tk.END)
            self.log_text.configure(state='disabled')
            
            # 简单的日志分析
            if "客户端已连接" in msg:
                self.client_label.config(text="客户端: 已连接", foreground="green")
            elif "客户端断开连接" in msg:
                self.client_label.config(text="客户端: 无连接", foreground="gray")
                
        self.root.after(100, self.process_log_queue)

    def launch_chrome_debug(self):
        try:
            bat_path = os.path.join(os.getcwd(), "start_chrome.bat")
            if os.path.exists(bat_path):
                subprocess.Popen(["cmd", "/c", "start", bat_path], shell=True)
                self.log(f"已调用: {bat_path}")
            else:
                messagebox.showerror("错误", "找不到 start_chrome.bat")
        except Exception as e:
            self.log(f"启动 Chrome 失败: {e}", "ERROR")

    def launch_chrome_clone(self):
        try:
            bat_path = os.path.join(os.getcwd(), "start_chrome_clone.bat")
            if os.path.exists(bat_path):
                subprocess.Popen(["cmd", "/c", "start", bat_path], shell=True)
                self.log(f"已调用: {bat_path}")
            else:
                messagebox.showerror("错误", "找不到 start_chrome_clone.bat")
        except Exception as e:
            self.log(f"启动 Chrome 失败: {e}", "ERROR")

    def toggle_server(self):
        if self.is_running:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self):
        port = self.port_var.get()
        token = self.token_var.get()
        
        if not port.isdigit():
            messagebox.showwarning("输入错误", "端口必须是数字")
            return

        # 设置环境变量
        env = os.environ.copy()
        env["AUTH_TOKEN"] = token
        env["PORT"] = port
        # 强制 Python 输出无缓冲
        env["PYTHONUNBUFFERED"] = "1"

        try:
            # 启动子进程
            # 关键：capture_output=False, stderr=subprocess.PIPE 让我们可以读取实时流
            # creationflags=subprocess.CREATE_NO_WINDOW 可以隐藏黑框 (Windows专用)，这里为了调试方便先不加，或者设为0
            cmd = ["python", "server_b.py"]
            self.process = subprocess.Popen(
                cmd, 
                env=env,
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, # 将 stderr 归并到 stdout
                text=True, 
                encoding="utf-8", # 强制使用 utf-8 解码，解决 GBK 报错
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW # 隐藏黑框
            )
            
            self.is_running = True
            self.start_btn.config(text="停止服务器 (Stop)")
            self.status_label.config(text=f"状态: 运行中 (Port {port})", foreground="green")
            self.log(f"正在启动服务器... 端口: {port}, Token: {token}")

            # 开启线程读取日志
            threading.Thread(target=self.read_process_output, args=(self.process,), daemon=True).start()

        except Exception as e:
            self.log(f"启动失败: {e}", "ERROR")
            self.is_running = False

    def stop_server(self):
        if self.process:
            self.log("正在停止服务器...")
            self.process.terminate()
            self.process = None
        
        self.is_running = False
        self.start_btn.config(text="启动服务器 (Start)")
        self.status_label.config(text="状态: 已停止", foreground="red")
        self.client_label.config(text="客户端: 无连接", foreground="gray")

    def read_process_output(self, process):
        """后台线程：实时读取子进程输出"""
        try:
            while self.is_running and process.poll() is None:
                line = process.stdout.readline()
                if line:
                    self.log(line.strip())
        except Exception as e:
            self.log(f"日志读取中断: {e}", "ERROR")

    def on_close(self):
        if self.is_running:
            if messagebox.askokcancel("退出", "服务器正在运行，确定要退出吗？"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    # 尝试设置图标 (可选)
    # root.iconbitmap("icon.ico") 
    app = ServerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
