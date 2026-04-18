"""
主窗口
"""

import webbrowser
import customtkinter as ctk
from (Deprecated)_gui.styles import COLORS, FONTS, SIZES


class MainWindow(ctk.CTk):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 窗口设置
        self.title("B站下载器 v1.0")
        self.geometry(f"{SIZES['window_width']}x{SIZES['window_height']}")
        self.minsize(800, 600)
        
        # 创建主框架
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=SIZES['padding'], pady=SIZES['padding'])
        
        # 创建标题
        self.create_title()
        
        # 创建标签页
        self.create_tabview()
        
        # 创建状态栏（在标签页之后）
        self.create_status_bar()
    
    def create_title(self):
        """创建标题区域"""
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, SIZES['padding']))
        
        # 标题
        title_label = ctk.CTkLabel(
            title_frame,
            text="🎵 B站下载器",
            font=FONTS["title"],
            text_color=COLORS["primary"]
        )
        title_label.pack(side="left")
        
        # 版本信息
        version_label = ctk.CTkLabel(
            title_frame,
            text="v1.0.0 | 支持视频/音频下载",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        version_label.pack(side="right")
    
    def create_tabview(self):
        """创建标签页"""
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True)
        
        # 添加标签页
        self.tabview.add("📥 下载")
        self.tabview.add("⚙️ 设置")
        self.tabview.add("📊 任务")
        self.tabview.add("ℹ️ 关于")
        
        # 先创建任务标签页的内容（确保 tasks_text 存在）
        self.create_tasks_tab()
        
        # 再创建其他标签页
        self.create_about_tab()
        
        # 最后创建需要后端的标签页（延迟初始化）
        from gui.download_tab import DownloadTab
        from gui.settings_tab import SettingsTab
        
        self.download_tab = DownloadTab(self.tabview.tab("📥 下载"), self)
        self.settings_tab = SettingsTab(self.tabview.tab("⚙️ 设置"), self)
    
    def create_tasks_tab(self):
        """创建任务标签页"""
        tasks_frame = self.tabview.tab("📊 任务")
        
        # 任务列表
        self.tasks_text = ctk.CTkTextbox(tasks_frame, font=FONTS["code"])
        self.tasks_text.pack(fill="both", expand=True, padx=SIZES['small_padding'], pady=SIZES['small_padding'])
        
        # 按钮框架
        btn_frame = ctk.CTkFrame(tasks_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=SIZES['small_padding'], pady=SIZES['small_padding'])
        
        clear_btn = ctk.CTkButton(
            btn_frame,
            text="清空日志",
            command=self.clear_tasks,
            height=30,
            width=100
        )
        clear_btn.pack(side="right", padx=5)
    
    def create_about_tab(self):
        """创建关于标签页"""
        about_frame = self.tabview.tab("ℹ️ 关于")
        
        # 创建可滚动框架
        scroll_frame = ctk.CTkScrollableFrame(about_frame)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Logo/标题
        title_label = ctk.CTkLabel(
            scroll_frame,
            text="🎵 B站下载器",
            font=("Microsoft YaHei", 28, "bold"),
            text_color=COLORS["primary"]
        )
        title_label.pack(pady=(20, 5))
        
        version_label = ctk.CTkLabel(
            scroll_frame,
            text="版本 1.0.0",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        version_label.pack()
        
        # 分隔线
        separator = ctk.CTkFrame(scroll_frame, height=2, fg_color=COLORS["border"])
        separator.pack(fill="x", pady=20)
        
        # 功能特性
        features_title = ctk.CTkLabel(
            scroll_frame,
            text="✨ 功能特性",
            font=FONTS["heading"],
            anchor="w"
        )
        features_title.pack(anchor="w", pady=(10, 10))
        
        features = [
            "• 支持视频/音频下载",
            "• 支持收藏夹批量下载",
            "• 支持多线程并行下载",
            "• 可自定义文件名格式",
            "• 支持搜索和BV号下载",
            "• 支持公开/私密收藏夹"
        ]
        
        for feature in features:
            f_label = ctk.CTkLabel(
                scroll_frame,
                text=feature,
                font=FONTS["body"],
                anchor="w"
            )
            f_label.pack(anchor="w", pady=2)
        
        # 分隔线
        separator2 = ctk.CTkFrame(scroll_frame, height=2, fg_color=COLORS["border"])
        separator2.pack(fill="x", pady=20)
        
        # 技术栈
        tech_title = ctk.CTkLabel(
            scroll_frame,
            text="🛠️ 技术栈",
            font=FONTS["heading"],
            anchor="w"
        )
        tech_title.pack(anchor="w", pady=(10, 10))
        
        tech = [
            "• Python 3.10+",
            "• CustomTkinter (GUI)",
            "• FFmpeg (音视频处理)",
            "• aiohttp (异步下载)"
        ]
        
        for t in tech:
            t_label = ctk.CTkLabel(
                scroll_frame,
                text=t,
                font=FONTS["body"],
                anchor="w"
            )
            t_label.pack(anchor="w", pady=2)
        
        # 分隔线
        separator3 = ctk.CTkFrame(scroll_frame, height=2, fg_color=COLORS["border"])
        separator3.pack(fill="x", pady=20)
        
        # 链接按钮区域
        links_title = ctk.CTkLabel(
            scroll_frame,
            text="🔗 相关链接",
            font=FONTS["heading"],
            anchor="w"
        )
        links_title.pack(anchor="w", pady=(10, 10))
        
        # 按钮框架
        links_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        links_frame.pack(fill="x", pady=10)
        
        # GitHub按钮
        github_btn = ctk.CTkButton(
            links_frame,
            text="📂 GitHub 仓库",
            command=self.open_github,
            height=35,
            width=150,
            fg_color="#333333",
            hover_color="#444444"
        )
        github_btn.pack(side="left", padx=10)
        
        # 文档按钮
        docs_btn = ctk.CTkButton(
            links_frame,
            text="📖 使用文档",
            command=self.open_docs,
            height=35,
            width=150,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"]
        )
        docs_btn.pack(side="left", padx=10)
        
        # 反馈按钮
        feedback_btn = ctk.CTkButton(
            links_frame,
            text="💬 问题反馈",
            command=self.open_issues,
            height=35,
            width=150,
            fg_color="#722ED1",
            hover_color="#8B3FF0"
        )
        feedback_btn.pack(side="left", padx=10)
        
        # 贡献者信息
        separator4 = ctk.CTkFrame(scroll_frame, height=2, fg_color=COLORS["border"])
        separator4.pack(fill="x", pady=20)
        
        contributors_label = ctk.CTkLabel(
            scroll_frame,
            text="👥 贡献者",
            font=FONTS["heading"],
            anchor="w"
        )
        contributors_label.pack(anchor="w", pady=(10, 10))
        
        contributors_text = ctk.CTkLabel(
            scroll_frame,
            text="罗逸琳 (Buelier, LUO Yiling)  |  DeepSeek",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        contributors_text.pack()
        
        # 版权信息
        copyright_label = ctk.CTkLabel(
            scroll_frame,
            text="© 2024 B站下载器 | 仅供学习交流使用",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        copyright_label.pack(pady=(20, 10))

    def open_github(self):
        """打开GitHub仓库"""
        import webbrowser
        webbrowser.open("https://github.com/Buelier/bili-downloader")

    def open_docs(self):
        """打开使用文档"""
        import webbrowser
        webbrowser.open("https://github.com/Buelier/bili-downloader/wiki")

    def open_issues(self):
        """打开问题反馈页面"""
        import webbrowser
        webbrowser.open("https://github.com/Buelier/bili-downloader/issues")
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_frame = ctk.CTkFrame(self.main_frame, height=30)
        self.status_frame.pack(fill="x", pady=(SIZES['small_padding'], 0))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="就绪",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(side="left", padx=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, width=200)
        self.progress_bar.pack(side="right", padx=10)
        self.progress_bar.set(0)
    
    def update_status(self, message: str, progress: float = None):
        """更新状态栏"""
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)
        self.update_idletasks()
    
    def log_message(self, message: str):
        """添加日志消息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        # 确保 tasks_text 存在
        if hasattr(self, 'tasks_text') and self.tasks_text is not None:
            self.tasks_text.insert("end", f"[{timestamp}] {message}\n")
            self.tasks_text.see("end")
        else:
            print(f"[{timestamp}] {message}")
        self.update_idletasks()
    
    def clear_tasks(self):
        """清空任务日志"""
        if hasattr(self, 'tasks_text') and self.tasks_text is not None:
            self.tasks_text.delete("1.0", "end")