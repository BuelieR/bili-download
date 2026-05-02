"""
设置标签页
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from _Deprecated_gui._Deprecated_styles import COLORS, FONTS, SIZES


class SettingsTab:
    """设置标签页类"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.config = None
        
        # 延迟初始化配置
        self.init_config()
        
        # 创建UI
        self.create_ui()
    
    def init_config(self):
        """初始化配置"""
        try:
            from config import Config
            self.config = Config()
        except Exception as e:
            self.app.log_message(f"加载配置失败: {e}")
    
    def create_ui(self):
        """创建UI"""
        # 滚动框架
        scroll_frame = ctk.CTkScrollableFrame(self.parent)
        scroll_frame.pack(fill="both", expand=True, padx=SIZES['padding'], pady=SIZES['padding'])
        
        # 保存目录
        self.create_dir_section(scroll_frame)
        
        # 下载设置
        self.create_download_section(scroll_frame)
        
        # 文件名格式
        self.create_filename_section(scroll_frame)
        
        # Cookie设置
        self.create_cookie_section(scroll_frame)
        
        # 按钮区域
        self.create_button_section(scroll_frame)
    
    def create_dir_section(self, parent):
        """创建目录设置区域"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, SIZES['padding']))
        
        label = ctk.CTkLabel(section, text="📁 保存目录", font=FONTS["heading"])
        label.pack(anchor="w", padx=SIZES['small_padding'], pady=(SIZES['small_padding'], 5))
        
        dir_frame = ctk.CTkFrame(section, fg_color="transparent")
        dir_frame.pack(fill="x", padx=SIZES['small_padding'], pady=5)
        
        self.dir_entry = ctk.CTkEntry(
            dir_frame,
            height=SIZES['entry_height'],
            width=500
        )
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        browse_btn = ctk.CTkButton(
            dir_frame,
            text="浏览",
            command=self.browse_directory,
            width=80,
            height=SIZES['button_height']
        )
        browse_btn.pack(side="right")
        
        # 加载当前设置
        if self.config:
            self.dir_entry.insert(0, self.config.get('save_dir', ''))
    
    def create_download_section(self, parent):
        """创建设置区域"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, SIZES['padding']))
        
        label = ctk.CTkLabel(section, text="⚡ 下载设置", font=FONTS["heading"])
        label.pack(anchor="w", padx=SIZES['small_padding'], pady=(SIZES['small_padding'], 5))
        
        # 并行数量
        parallel_frame = ctk.CTkFrame(section, fg_color="transparent")
        parallel_frame.pack(fill="x", padx=SIZES['small_padding'], pady=5)
        
        ctk.CTkLabel(parallel_frame, text="并行下载数量:", width=120).pack(side="left")
        self.parallel_entry = ctk.CTkEntry(parallel_frame, width=80, height=SIZES['entry_height'])
        self.parallel_entry.pack(side="left", padx=10)
        ctk.CTkLabel(parallel_frame, text="(1-10)", font=FONTS["small"]).pack(side="left")
        
        # 速度限制
        speed_frame = ctk.CTkFrame(section, fg_color="transparent")
        speed_frame.pack(fill="x", padx=SIZES['small_padding'], pady=5)
        
        ctk.CTkLabel(speed_frame, text="速度限制 (MB/s):", width=120).pack(side="left")
        self.speed_entry = ctk.CTkEntry(speed_frame, width=80, height=SIZES['entry_height'])
        self.speed_entry.pack(side="left", padx=10)
        ctk.CTkLabel(speed_frame, text="(0表示不限速)", font=FONTS["small"]).pack(side="left")
        
        # 加载当前设置
        if self.config:
            self.parallel_entry.insert(0, str(self.config.get('max_parallel', 3)))
            self.speed_entry.insert(0, str(self.config.get('max_speed_mbps', 0)))
    
    def create_filename_section(self, parent):
        """创建文件名格式设置区域"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, SIZES['padding']))
        
        label = ctk.CTkLabel(section, text="📝 文件名格式", font=FONTS["heading"])
        label.pack(anchor="w", padx=SIZES['small_padding'], pady=(SIZES['small_padding'], 5))
        
        # 变量说明
        vars_text = """可用变量:
${video_name} - 视频名称
${video_author} - 视频作者  
${video_time} - 发布时间
${download_time} - 下载时间
${ID} - 重名编号"""
        
        vars_label = ctk.CTkLabel(section, text=vars_text, font=FONTS["small"], justify="left")
        vars_label.pack(anchor="w", padx=SIZES['small_padding'], pady=5)
        
        self.format_entry = ctk.CTkEntry(
            section,
            height=SIZES['entry_height'],
            width=500
        )
        self.format_entry.pack(fill="x", padx=SIZES['small_padding'], pady=5)
        
        # 加载当前设置
        if self.config:
            self.format_entry.insert(0, self.config.get('filename_format', ''))
    
    def create_cookie_section(self, parent):
        """创建Cookie设置区域"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=(0, SIZES['padding']))
        
        label = ctk.CTkLabel(section, text="🔐 登录设置 (SESSDATA)", font=FONTS["heading"])
        label.pack(anchor="w", padx=SIZES['small_padding'], pady=(SIZES['small_padding'], 5))
        
        self.cookie_entry = ctk.CTkEntry(
            section,
            placeholder_text="输入SESSDATA...",
            height=SIZES['entry_height'],
            show="*"
        )
        self.cookie_entry.pack(fill="x", padx=SIZES['small_padding'], pady=5)
        
        # 提示信息
        tip_label = ctk.CTkLabel(
            section,
            text="提示：SESSDATA用于下载私密内容，从浏览器开发者工具中获取",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        tip_label.pack(anchor="w", padx=SIZES['small_padding'], pady=5)
        
        # 加载当前设置
        if self.config:
            cookie = self.config.get('cookie', '')
            if cookie:
                self.cookie_entry.insert(0, "***已设置***")
    
    def create_button_section(self, parent):
        """创建按钮区域"""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=SIZES['padding'])
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 保存设置",
            command=self.save_settings,
            height=40,
            width=120,
            fg_color=COLORS["success"]
        )
        save_btn.pack(side="left", padx=5)
        
        reset_btn = ctk.CTkButton(
            btn_frame,
            text="↺ 重置",
            command=self.reset_settings,
            height=40,
            width=80
        )
        reset_btn.pack(side="left", padx=5)
    
    def browse_directory(self):
        """浏览目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)
    
    def save_settings(self):
        """保存设置"""
        if not self.config:
            messagebox.showerror("错误", "配置模块未初始化")
            return
        
        try:
            # 保存目录
            save_dir = self.dir_entry.get().strip()
            if save_dir:
                self.config.set('save_dir', save_dir)
            
            # 并行数量
            parallel = self.parallel_entry.get().strip()
            if parallel:
                self.config.set('max_parallel', int(parallel))
            
            # 速度限制
            speed = self.speed_entry.get().strip()
            if speed:
                self.config.set('max_speed_mbps', float(speed))
            
            # 文件名格式
            filename_format = self.format_entry.get().strip()
            if filename_format:
                self.config.set('filename_format', filename_format)
            
            # Cookie - 只有输入了新值才更新
            cookie = self.cookie_entry.get().strip()
            if cookie and cookie != "***已设置***":
                self.config.set('cookie', cookie)
            
            messagebox.showinfo("成功", "设置已保存")
            self.app.log_message("设置已保存")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def reset_settings(self):
        """重置设置"""
        if messagebox.askyesno("确认", "确认重置所有设置？"):
            if self.config and self.config.config_path.exists():
                self.config.config_path.unlink()
            messagebox.showinfo("成功", "设置已重置，请重启程序")