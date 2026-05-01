import tkinter as tk
from tkinter import ttk, filedialog
from _Deprecated_gui._Deprecated_styles import AppStyles, CustomWidgets

class DownloadPanel:
    """下载面板"""
    
    def __init__(self, parent, download_callback):
        self.parent = parent
        self.download_callback = download_callback
        self.active_downloads = {}
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建下载界面"""
        # 主框架
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(main_frame, text="📥 下载器", style='Title.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # 输入区域
        self.create_input_area(main_frame)
        
        # 下载队列区域
        self.create_queue_area(main_frame)
        
        # 下载控制区域
        self.create_control_area(main_frame)
    
    def create_input_area(self, parent):
        """创建输入区域"""
        card = CustomWidgets.create_card(parent)
        card.pack(fill=tk.X, pady=(0, 15))
        
        title = ttk.Label(card, text="输入BV号或链接", style='Heading.TLabel')
        title.pack(anchor=tk.W, padx=15, pady=(15, 10))
        
        # URL输入
        url_frame = ttk.Frame(card)
        url_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        download_btn = ttk.Button(url_frame, text="下载", 
                                 style='Accent.TButton',
                                 command=self.add_download)
        download_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 格式选择
        format_frame = ttk.Frame(card)
        format_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Label(format_frame, text="下载格式:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="mp4")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var,
                                   values=["仅视频(mp4)", "仅音乐(mp3)", "音频(mp4)"],
                                   width=15)
        format_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # 文件选择按钮
        file_frame = ttk.Frame(card)
        file_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        txt_btn = ttk.Button(file_frame, text="从TXT文件导入",
                            command=self.load_from_txt)
        txt_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        fav_btn = ttk.Button(file_frame, text="下载收藏夹",
                            command=self.download_favorites)
        fav_btn.pack(side=tk.LEFT)
    
    def create_queue_area(self, parent):
        """创建下载队列区域"""
        card = CustomWidgets.create_card(parent)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        title_frame = ttk.Frame(card)
        title_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        title = ttk.Label(title_frame, text="下载队列", style='Heading.TLabel')
        title.pack(side=tk.LEFT)
        
        # 清空按钮
        clear_btn = ttk.Button(title_frame, text="清空已完成",
                              command=self.clear_completed)
        clear_btn.pack(side=tk.RIGHT)
        
        # 创建Canvas和Scrollbar用于滚动
        canvas_frame = ttk.Frame(card)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.canvas = tk.Canvas(canvas_frame, bg=AppStyles.COLORS['bg_medium'],
                               highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical",
                                 command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind("<Configure>", 
                                   lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 鼠标滚轮绑定
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
    
    def create_control_area(self, parent):
        """创建控制区域"""
        card = CustomWidgets.create_card(parent)
        card.pack(fill=tk.X)
        
        control_frame = ttk.Frame(card)
        control_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # 全局进度条
        self.global_progress = ttk.Progressbar(control_frame, mode='determinate')
        self.global_progress.pack(fill=tk.X, pady=(0, 10))
        
        # 控制按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        self.pause_all_btn = ttk.Button(button_frame, text="全部暂停",
                                       command=self.pause_all)
        self.pause_all_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.resume_all_btn = ttk.Button(button_frame, text="全部继续",
                                        command=self.resume_all)
        self.resume_all_btn.pack(side=tk.LEFT)
        
        # 统计信息
        self.stats_label = ttk.Label(control_frame, text="等待下载: 0 | 已完成: 0",
                                    font=AppStyles.FONTS['small'])
        self.stats_label.pack(side=tk.RIGHT)
    
    def add_download(self):
        """添加下载任务"""
        url = self.url_var.get().strip()
        if url:
            download_format = self.format_var.get()
            if self.download_callback:
                self.download_callback(url, download_format, self.update_progress)
            self.url_var.set("")
    
    def load_from_txt(self):
        """从TXT文件导入"""
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                urls = f.read().strip().split('\n')
                for url in urls:
                    if url.strip():
                        self.download_callback(url.strip(), self.format_var.get(), 
                                              self.update_progress)
    
    def download_favorites(self):
        """下载收藏夹"""
        # 创建对话框询问收藏夹类型和ID
        dialog = tk.Toplevel(self.parent)
        dialog.title("下载收藏夹")
        dialog.geometry("400x200")
        dialog.configure(bg=AppStyles.COLORS['bg_dark'])
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # 内容
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="收藏夹类型:").pack(anchor=tk.W, pady=(0, 5))
        fav_type = ttk.Combobox(frame, values=["公开收藏夹", "私密收藏夹"], width=15)
        fav_type.pack(fill=tk.X, pady=(0, 15))
        fav_type.set("公开收藏夹")
        
        ttk.Label(frame, text="收藏夹ID:").pack(anchor=tk.W, pady=(0, 5))
        fav_id = ttk.Entry(frame)
        fav_id.pack(fill=tk.X, pady=(0, 20))
        
        def confirm():
            if fav_id.get():
                is_private = fav_type.get() == "私密收藏夹"
                self.download_callback(f"favorite:{fav_id.get()}:{is_private}",
                                      self.format_var.get(),
                                      self.update_progress)
                dialog.destroy()
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="确认", style='Accent.TButton',
                  command=confirm).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def update_progress(self, task_id, progress, status):
        """更新下载进度"""
        if task_id in self.active_downloads:
            widget = self.active_downloads[task_id]
            widget['progress'].set(progress)
            widget['status'].config(text=status)
            
            if progress >= 100:
                widget['status'].config(text="✓ 完成", 
                                       foreground=AppStyles.COLORS['success'])
    
    def add_task_to_queue(self, task_id, video_name):
        """添加任务到队列显示"""
        # 创建任务行
        task_frame = ttk.Frame(self.scrollable_frame)
        task_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 任务名称
        name_label = ttk.Label(task_frame, text=video_name[:50] + "...", 
                              font=AppStyles.FONTS['small'])
        name_label.pack(anchor=tk.W)
        
        # 进度条
        progress = ttk.Progressbar(task_frame, mode='determinate', length=300)
        progress.pack(fill=tk.X, pady=5)
        
        # 状态和控制
        control_frame = ttk.Frame(task_frame)
        control_frame.pack(fill=tk.X)
        
        status_label = ttk.Label(control_frame, text="等待中", 
                                font=AppStyles.FONTS['small'])
        status_label.pack(side=tk.LEFT)
        
        pause_btn = ttk.Button(control_frame, text="暂停", 
                              command=lambda: self.pause_task(task_id))
        pause_btn.pack(side=tk.RIGHT, padx=2)
        
        cancel_btn = ttk.Button(control_frame, text="取消",
                               command=lambda: self.cancel_task(task_id))
        cancel_btn.pack(side=tk.RIGHT)
        
        self.active_downloads[task_id] = {
            'frame': task_frame,
            'progress': progress,
            'status': status_label,
            'pause_btn': pause_btn,
            'cancel_btn': cancel_btn
        }
    
    def pause_task(self, task_id):
        """暂停任务"""
        if task_id in self.active_downloads:
            # 调用暂停功能
            pass
    
    def cancel_task(self, task_id):
        """取消任务"""
        if task_id in self.active_downloads:
            self.active_downloads[task_id]['frame'].destroy()
            del self.active_downloads[task_id]
    
    def pause_all(self):
        """暂停所有任务"""
        pass
    
    def resume_all(self):
        """继续所有任务"""
        pass
    
    def clear_completed(self):
        """清除已完成的任务"""
        for task_id in list(self.active_downloads.keys()):
            if self.active_downloads[task_id]['progress'].get() >= 100:
                self.active_downloads[task_id]['frame'].destroy()
                del self.active_downloads[task_id]
    
    def _on_mousewheel(self, event):
        """鼠标滚轮滚动"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")