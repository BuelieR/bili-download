import tkinter as tk
from tkinter import ttk, filedialog
import json
import os
from _Deprecated_gui._Deprecated_styles import AppStyles, CustomWidgets
from api.bili_api import BiliAPI

class SettingsPanel:
    """设置面板"""
    
    def __init__(self, parent, settings_callback):
        self.parent = parent
        self.settings_callback = settings_callback
        self.settings = {}
        
        # 创建主框架，使用pack并设置expand=True
        self.main_container = ttk.Frame(parent)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建Canvas和Scrollbar用于滚动（如果内容过多）
        self.create_scrollable_area()
        
        self.create_widgets()
        self.load_settings()
    
    def create_scrollable_area(self):
        """创建可滚动区域"""
        # 创建Canvas和滚动条
        self.canvas = tk.Canvas(self.main_container, 
                                bg=AppStyles.COLORS['bg_dark'],
                                highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", 
                                 command=self.canvas.yview)
        
        # 创建内部框架
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", 
                                   lambda e: self.canvas.configure(
                                       scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, 
                                 anchor="nw", width=self.canvas.winfo_reqwidth())
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定鼠标滚轮
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        
        # 绑定窗口大小改变事件
        self.canvas.bind('<Configure>', self._on_canvas_configure)
    
    def _on_canvas_configure(self, event):
        """当Canvas大小改变时，调整内部框架宽度"""
        self.canvas.itemconfig(1, width=event.width)
    
    def _on_mousewheel(self, event):
        """鼠标滚轮滚动"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_widgets(self):
        """创建设置界面"""
        # 主框架（在滚动区域内）
        main_frame = ttk.Frame(self.scrollable_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(main_frame, text="⚙️ 设置", style='Title.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # 创建卡片式设置区域
        self.create_download_settings(main_frame)
        self.create_format_settings(main_frame)
        self.create_advanced_settings(main_frame)
        
        # 按钮区域 - 固定在底部
        self.create_button_area(main_frame)
    
    def create_download_settings(self, parent):
        """下载设置区域"""
        card = CustomWidgets.create_card(parent)
        card.pack(fill=tk.X, pady=(0, 15))
        
        # 标题
        title = ttk.Label(card, text="下载设置", style='Heading.TLabel')
        title.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        # 保存目录
        dir_frame = ttk.Frame(card)
        dir_frame.pack(fill=tk.X, padx=15, pady=5)
        
        ttk.Label(dir_frame, text="保存目录:").pack(side=tk.LEFT)
        self.save_dir_var = tk.StringVar()
        save_dir_entry = ttk.Entry(dir_frame, textvariable=self.save_dir_var)
        save_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5))
        
        browse_btn = ttk.Button(dir_frame, text="浏览", 
                               command=self.browse_directory)
        browse_btn.pack(side=tk.LEFT)
        
        # 并行下载数
        parallel_frame = ttk.Frame(card)
        parallel_frame.pack(fill=tk.X, padx=15, pady=5)
        
        ttk.Label(parallel_frame, text="并行下载数:").pack(side=tk.LEFT)
        self.parallel_var = tk.IntVar(value=3)
        parallel_spin = ttk.Spinbox(parallel_frame, from_=1, to=10,
                                   textvariable=self.parallel_var, width=10)
        parallel_spin.pack(side=tk.LEFT, padx=(10, 0))
        
        # 速度限制
        speed_frame = ttk.Frame(card)
        speed_frame.pack(fill=tk.X, padx=15, pady=5)
        
        ttk.Label(speed_frame, text="速度限制:").pack(side=tk.LEFT)
        self.speed_var = tk.StringVar(value="0")
        speed_entry = ttk.Entry(speed_frame, textvariable=self.speed_var, width=15)
        speed_entry.pack(side=tk.LEFT, padx=(10, 5))
        
        self.speed_unit_var = tk.StringVar(value="KB/s")
        speed_unit = ttk.Combobox(speed_frame, textvariable=self.speed_unit_var,
                                 values=["KB/s", "MB/s", "GB/s"], width=8)
        speed_unit.pack(side=tk.LEFT)
        
        ttk.Label(speed_frame, text="(0表示无限制)").pack(side=tk.LEFT, padx=(10, 0))
    
    def create_format_settings(self, parent):
        """格式设置区域"""
        card = CustomWidgets.create_card(parent)
        card.pack(fill=tk.X, pady=(0, 15))
        
        title = ttk.Label(card, text="格式设置", style='Heading.TLabel')
        title.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        # 默认下载格式
        format_frame = ttk.Frame(card)
        format_frame.pack(fill=tk.X, padx=15, pady=5)
        
        ttk.Label(format_frame, text="默认下载格式:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="仅视频(mp4)")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var,
                                   values=["仅视频(mp4)", "仅音乐(mp3)", "音频(mp4)"], 
                                   width=20)
        format_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # 文件名格式
        name_frame = ttk.Frame(card)
        name_frame.pack(fill=tk.X, padx=15, pady=5)
        
        ttk.Label(name_frame, text="文件名格式:").pack(anchor=tk.W)
        
        name_entry = tk.Text(card, height=3, 
                            bg=AppStyles.COLORS['bg_light'],
                            fg=AppStyles.COLORS['text_primary'],
                            insertbackground='white',
                            font=AppStyles.FONTS['small'])
        name_entry.pack(fill=tk.X, padx=15, pady=(5, 10))
        self.name_format_text = name_entry
        
        # 提示
        hint_frame = ttk.Frame(card)
        hint_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        hint_text = "可用变量: ${video_name}, ${video_time}, ${video_author}, ${download_time}, ${ID}"
        hint_label = ttk.Label(hint_frame, text=hint_text, 
                              style='TLabel', font=AppStyles.FONTS['small'])
        hint_label.pack(anchor=tk.W)
    
    def create_advanced_settings(self, parent):
        """高级设置区域"""
        card = CustomWidgets.create_card(parent)
        card.pack(fill=tk.X, pady=(0, 15))
        
        title = ttk.Label(card, text="高级设置", style='Heading.TLabel')
        title.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        # Cookie设置
        cookie_frame = ttk.Frame(card)
        cookie_frame.pack(fill=tk.X, padx=15, pady=5)
        
        ttk.Label(cookie_frame, text="Cookie (SESSDATA, 登录后获取):").pack(anchor=tk.W)
        
        cookie_entry = tk.Text(card, height=4,
                              bg=AppStyles.COLORS['bg_light'],
                              fg=AppStyles.COLORS['text_primary'],
                              insertbackground='white',
                              font=AppStyles.FONTS['small'])
        cookie_entry.pack(fill=tk.X, padx=15, pady=(5, 15))
        self.cookie_text = cookie_entry
        
        # 添加一些空间
        ttk.Frame(card, height=10).pack()
    
    def create_button_area(self, parent):
        """创建按钮区域 - 固定在底部"""
        # 按钮容器
        button_container = ttk.Frame(parent)
        button_container.pack(fill=tk.X, pady=(20, 0))
        
        # 添加分隔线
        separator = ttk.Separator(button_container, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 15))
        
        # 按钮框架
        button_frame = ttk.Frame(button_container)
        button_frame.pack(fill=tk.X)
        
        # 保存按钮 - 主要按钮放在右边
        save_btn = ttk.Button(button_frame, text="💾 保存设置", 
                             style='Accent.TButton',
                             command=self.save_settings)
        save_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 重置按钮
        reset_btn = ttk.Button(button_frame, text="🔄 重置默认",
                              command=self.reset_settings)
        reset_btn.pack(side=tk.RIGHT)
        
        # 测试连接按钮（可选）
        test_btn = ttk.Button(button_frame, text="🔌 测试连接",
                             command=self.test_connection)
        test_btn.pack(side=tk.LEFT)
    
    def browse_directory(self):
        """浏览文件夹"""
        directory = filedialog.askdirectory()
        if directory:
            self.save_dir_var.set(directory)
    
    def load_settings(self):
        """加载设置"""
        if os.path.exists('settings.json'):
            with open('settings.json', 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
            
            # 填充到界面
            self.save_dir_var.set(self.settings.get('save_dir', ''))
            self.parallel_var.set(self.settings.get('max_parallel', 3))
            speed = self.settings.get('max_speed', 0)
            if isinstance(speed, (int, float)):
                self.speed_var.set(str(speed))
            self.name_format_text.delete('1.0', tk.END)
            self.name_format_text.insert('1.0', 
                self.settings.get('name_format', '${video_name}_AUTHOR_${video_author}'))
            self.cookie_text.delete('1.0', tk.END)
            self.cookie_text.insert('1.0', self.settings.get('cookie', ''))
        else:
            # 默认值
            self.name_format_text.delete('1.0', tk.END)
            self.name_format_text.insert('1.0', '${video_name}_AUTHOR_${video_author}')
    
    def save_settings(self):
        """保存设置"""
        self.settings = {
            'save_dir': self.save_dir_var.get(),
            'max_parallel': self.parallel_var.get(),
            'max_speed': float(self.speed_var.get()) if self.speed_var.get() else 0,
            'speed_unit': self.speed_unit_var.get(),
            'default_format': self.format_var.get(),
            'name_format': self.name_format_text.get('1.0', 'end-1c').strip(),
            'cookie': self.cookie_text.get('1.0', 'end-1c').strip()
        }
        
        try:
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            
            if self.settings_callback:
                self.settings_callback(self.settings)
            
            self.show_message("✅ 设置已保存", "success")
        except Exception as e:
            self.show_message(f"❌ 保存失败: {str(e)}", "error")
    
    def reset_settings(self):
        """重置设置"""
        self.save_dir_var.set("")
        self.parallel_var.set(3)
        self.speed_var.set("0")
        self.speed_unit_var.set("KB/s")
        self.format_var.set("仅视频(mp4)")
        self.name_format_text.delete('1.0', tk.END)
        self.name_format_text.insert('1.0', '${video_name}_AUTHOR_${video_author}')
        self.cookie_text.delete('1.0', tk.END)
        
        self.show_message("🔄 已重置为默认设置", "info")
    
    def test_connection(self):
        """测试B站连接"""
        import threading
        
        def test():
            try:
                cookie = self.cookie_text.get('1.0', 'end-1c').strip()
                api = BiliAPI(cookie=cookie if cookie else None)
                
                # 测试获取用户信息
                user_info = api.get_user_info()
                if user_info:
                    self.show_message(f"✅ 连接成功！欢迎: {user_info.get('name', '用户')}", "success")
                else:
                    self.show_message("⚠️ 连接成功但未登录，部分功能受限", "warning")
            except Exception as e:
                self.show_message(f"❌ 连接失败: {str(e)}", "error")
        
        self.show_message("🔄 正在测试连接...", "info")
        threading.Thread(target=test, daemon=True).start()
    
    def show_message(self, message, type='info'):
        """显示临时消息"""
        # 创建临时提示窗口
        from tkinter import messagebox
        
        if type == 'error':
            messagebox.showerror("错误", message)
        elif type == 'warning':
            messagebox.showwarning("警告", message)
        elif type == 'info':
            messagebox.showinfo("提示", message)
        else:
            # 在状态栏显示（如果有的话）
            print(f"[{type.upper()}] {message}")
    
    def get_settings(self):
        """获取当前设置"""
        return {
            'save_dir': self.save_dir_var.get(),
            'max_parallel': self.parallel_var.get(),
            'max_speed': float(self.speed_var.get()) if self.speed_var.get() else 0,
            'speed_unit': self.speed_unit_var.get(),
            'default_format': self.format_var.get(),
            'name_format': self.name_format_text.get('1.0', 'end-1c').strip(),
            'cookie': self.cookie_text.get('1.0', 'end-1c').strip()
        }