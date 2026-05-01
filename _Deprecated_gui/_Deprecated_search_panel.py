import tkinter as tk
from tkinter import ttk
from _Deprecated_gui._Deprecated_styles import AppStyles, CustomWidgets

class SearchPanel:
    """搜索面板"""
    
    def __init__(self, parent, search_callback, download_callback):
        self.parent = parent
        self.search_callback = search_callback
        self.download_callback = download_callback
        self.current_page = 0
        self.search_results = []
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建搜索界面"""
        # 主框架
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🔍 视频搜索", style='Title.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # 搜索区域
        self.create_search_area(main_frame)
        
        # 结果区域
        self.create_results_area(main_frame)
        
        # 分页区域
        self.create_pagination_area(main_frame)
    
    def create_search_area(self, parent):
        """创建搜索区域"""
        card = CustomWidgets.create_card(parent)
        card.pack(fill=tk.X, pady=(0, 15))
        
        search_frame = ttk.Frame(card)
        search_frame.pack(fill=tk.X, padx=15, pady=15)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var,
                                font=AppStyles.FONTS['normal'])
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        search_btn = ttk.Button(search_frame, text="搜索", 
                               style='Accent.TButton',
                               command=self.perform_search)
        search_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 绑定回车键
        search_entry.bind('<Return>', lambda e: self.perform_search())
    
    def create_results_area(self, parent):
        """创建结果显示区域"""
        card = CustomWidgets.create_card(parent)
        card.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview
        columns = ('#', '标题', '作者', 'BV号')
        self.tree = ttk.Treeview(card, columns=columns, show='headings',
                                height=15, selectmode='browse')
        
        # 设置列
        self.tree.heading('#', text='序号', anchor=tk.CENTER)
        self.tree.heading('标题', text='标题', anchor=tk.W)
        self.tree.heading('作者', text='作者', anchor=tk.W)
        self.tree.heading('BV号', text='BV号', anchor=tk.CENTER)
        
        self.tree.column('#', width=50, anchor=tk.CENTER)
        self.tree.column('标题', width=400, anchor=tk.W)
        self.tree.column('作者', width=150, anchor=tk.W)
        self.tree.column('BV号', width=120, anchor=tk.CENTER)
        
        # 滚动条
        vsb = ttk.Scrollbar(card, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(card, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky='nsew', padx=(15, 0), pady=15)
        vsb.grid(row=0, column=1, sticky='ns', pady=15, padx=(0, 15))
        hsb.grid(row=1, column=0, sticky='ew', padx=(15, 0))
        
        card.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure(0, weight=1)
        
        # 双击下载
        self.tree.bind('<Double-Button-1>', self.on_double_click)
        
        # 右键菜单
        self.create_context_menu()
    
    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.tree, tearoff=0,
                                   bg=AppStyles.COLORS['bg_light'],
                                   fg=AppStyles.COLORS['text_primary'])
        self.context_menu.add_command(label="下载此视频", command=self.download_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="复制BV号", command=self.copy_bvid)
        
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    def create_pagination_area(self, parent):
        """创建分页区域"""
        card = CustomWidgets.create_card(parent)
        card.pack(fill=tk.X, pady=(15, 0))
        
        pagination_frame = ttk.Frame(card)
        pagination_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # 上一页
        self.prev_btn = ttk.Button(pagination_frame, text="◀ 上一页",
                                  command=self.prev_page)
        self.prev_btn.pack(side=tk.LEFT)
        
        # 页码显示
        self.page_label = ttk.Label(pagination_frame, text="第 1 页",
                                   font=AppStyles.FONTS['normal'])
        self.page_label.pack(side=tk.LEFT, expand=True)
        
        # 下一页
        self.next_btn = ttk.Button(pagination_frame, text="下一页 ▶",
                                  command=self.next_page)
        self.next_btn.pack(side=tk.RIGHT)
        
        # 初始禁用
        self.prev_btn.config(state='disabled')
        self.next_btn.config(state='disabled')
    
    def perform_search(self):
        """执行搜索"""
        keyword = self.search_var.get().strip()
        if not keyword:
            return
        
        # 调用搜索回调
        if self.search_callback:
            self.search_results = self.search_callback(keyword)
            self.current_page = 0
            self.display_results()
    
    def display_results(self):
        """显示搜索结果"""
        # 清空现有结果
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 计算当前页的数据
        start = self.current_page * 15
        end = start + 15
        page_results = self.search_results[start:end]
        
        # 显示结果
        for idx, video in enumerate(page_results, start=1):
            self.tree.insert('', 'end', values=(
                idx,
                video.get('title', '未知标题')[:50],
                video.get('author', '未知作者'),
                video.get('bvid', '')
            ), tags=(video.get('bvid', ''),))
        
        # 更新分页按钮状态
        total_pages = (len(self.search_results) + 14) // 15
        self.page_label.config(text=f"第 {self.current_page + 1} / {total_pages} 页")
        
        self.prev_btn.config(state='normal' if self.current_page > 0 else 'disabled')
        self.next_btn.config(state='normal' if end < len(self.search_results) else 'disabled')
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_results()
    
    def next_page(self):
        """下一页"""
        if (self.current_page + 1) * 15 < len(self.search_results):
            self.current_page += 1
            self.display_results()
    
    def on_double_click(self, event):
        """双击下载"""
        self.download_selected()
    
    def download_selected(self):
        """下载选中的视频"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            bvid = item['tags'][0] if item['tags'] else None
            if bvid and self.download_callback:
                # 弹出格式选择对话框
                self.show_format_dialog(bvid)
    
    def show_format_dialog(self, bvid):
        """显示格式选择对话框"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("选择下载格式")
        dialog.geometry("300x200")
        dialog.configure(bg=AppStyles.COLORS['bg_dark'])
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # 居中
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="选择下载格式:").pack(pady=(0, 10))
        
        format_var = tk.StringVar(value="仅视频(mp4)")
        format_combo = ttk.Combobox(frame, textvariable=format_var,
                                   values=["仅视频(mp4)", "仅音乐(mp3)", "音频(mp4)"],
                                   width=15)
        format_combo.pack(pady=(0, 20))
        
        def confirm():
            self.download_callback(bvid, format_var.get(), None)
            dialog.destroy()
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="确认", style='Accent.TButton',
                  command=confirm).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def copy_bvid(self):
        """复制BV号"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            bvid = item['tags'][0] if item['tags'] else ''
            if bvid:
                self.parent.clipboard_clear()
                self.parent.clipboard_append(bvid)
                # 可以显示提示
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)