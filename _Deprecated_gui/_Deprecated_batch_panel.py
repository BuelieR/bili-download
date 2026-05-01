import tkinter as tk
from tkinter import ttk, filedialog
from _Deprecated_gui._Deprecated_styles import AppStyles, CustomWidgets

class BatchPanel:
    """批量处理面板"""
    
    def __init__(self, parent, batch_callback):
        self.parent = parent
        self.batch_callback = batch_callback
        self.batch_list = []
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建批量处理界面"""
        # 主框架 - 使用 pack
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ttk.Label(main_frame, text="📋 批量处理", style='Title.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # 输入区域
        self.create_input_area(main_frame)
        
        # 列表区域
        self.create_list_area(main_frame)
        
        # 控制区域
        self.create_control_area(main_frame)
    
    def create_input_area(self, parent):
        """创建输入区域"""
        card = CustomWidgets.create_card(parent)
        card.pack(fill=tk.X, pady=(0, 15))
        
        # 文本输入
        input_frame = ttk.Frame(card)
        input_frame.pack(fill=tk.X, padx=15, pady=15)
        
        ttk.Label(input_frame, text="批量输入(BV号/链接，每行一个):").pack(anchor=tk.W)
        
        self.batch_text = tk.Text(card, height=6,
                                 bg=AppStyles.COLORS['bg_light'],
                                 fg=AppStyles.COLORS['text_primary'],
                                 insertbackground='white',
                                 font=AppStyles.FONTS['small'])
        self.batch_text.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        # 按钮区域
        btn_frame = ttk.Frame(card)
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        add_btn = ttk.Button(btn_frame, text="添加到列表", style='Accent.TButton',
                            command=self.add_to_list)
        add_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        import_btn = ttk.Button(btn_frame, text="从文件导入",
                               command=self.import_from_file)
        import_btn.pack(side=tk.LEFT)
        
        clear_btn = ttk.Button(btn_frame, text="清空输入",
                              command=lambda: self.batch_text.delete('1.0', tk.END))
        clear_btn.pack(side=tk.RIGHT)
    
    def create_list_area(self, parent):
        """创建列表区域"""
        card = CustomWidgets.create_card(parent)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        title_frame = ttk.Frame(card)
        title_frame.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        title = ttk.Label(title_frame, text="下载列表", style='Heading.TLabel')
        title.pack(side=tk.LEFT)
        
        self.count_label = ttk.Label(title_frame, text=f"共 {len(self.batch_list)} 项",
                                    style='TLabel')
        self.count_label.pack(side=tk.RIGHT)
        
        # 创建容器框架用于 Treeview 和滚动条 - 使用 pack
        tree_container = ttk.Frame(card)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # 创建Treeview
        columns = ('序号', 'BV号/链接', '状态')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings',
                                height=10, selectmode='extended')
        
        self.tree.heading('序号', text='序号', anchor=tk.CENTER)
        self.tree.heading('BV号/链接', text='BV号/链接', anchor=tk.W)
        self.tree.heading('状态', text='状态', anchor=tk.CENTER)
        
        self.tree.column('序号', width=50, anchor=tk.CENTER)
        self.tree.column('BV号/链接', width=400, anchor=tk.W)
        self.tree.column('状态', width=100, anchor=tk.CENTER)
        
        # 滚动条
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        # 使用 pack 而不是 grid
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 右键菜单
        self.create_context_menu()
    
    def create_control_area(self, parent):
        """创建控制区域"""
        card = CustomWidgets.create_card(parent)
        card.pack(fill=tk.X)
        
        control_frame = ttk.Frame(card)
        control_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # 格式选择
        format_frame = ttk.Frame(control_frame)
        format_frame.pack(side=tk.LEFT)
        
        ttk.Label(format_frame, text="下载格式:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="仅视频(mp4)")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var,
                                   values=["仅视频(mp4)", "仅音乐(mp3)", "音频(mp4)"],
                                   width=15)
        format_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # 按钮区域
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        start_btn = ttk.Button(btn_frame, text="开始批量下载", style='Success.TButton',
                              command=self.start_batch)
        start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_btn = ttk.Button(btn_frame, text="移除选中",
                               command=self.remove_selected)
        remove_btn.pack(side=tk.LEFT)
    
    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.tree, tearoff=0,
                                   bg=AppStyles.COLORS['bg_light'],
                                   fg=AppStyles.COLORS['text_primary'])
        self.context_menu.add_command(label="移除选中", command=self.remove_selected)
        self.context_menu.add_command(label="清空列表", command=self.clear_list)
        
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    def add_to_list(self):
        """添加到列表"""
        text = self.batch_text.get('1.0', tk.END).strip()
        if text:
            items = text.split('\n')
            for item in items:
                item = item.strip()
                if item and item not in self.batch_list:
                    self.batch_list.append(item)
                    self.tree.insert('', 'end', values=(
                        len(self.batch_list),
                        item,
                        '等待中'
                    ))
            self.batch_text.delete('1.0', tk.END)
            self.update_count()
    
    def import_from_file(self):
        """从文件导入"""
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line and line not in self.batch_list:
                        self.batch_list.append(line)
                        self.tree.insert('', 'end', values=(
                            len(self.batch_list),
                            line,
                            '等待中'
                        ))
            self.update_count()
    
    def remove_selected(self):
        """移除选中的项"""
        selected = self.tree.selection()
        for item in selected:
            values = self.tree.item(item)['values']
            if values:
                # 从列表中移除
                url = values[1]
                if url in self.batch_list:
                    self.batch_list.remove(url)
            self.tree.delete(item)
        
        # 重新编号
        self.reindex()
        self.update_count()
    
    def clear_list(self):
        """清空列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.batch_list.clear()
        self.update_count()
    
    def reindex(self):
        """重新编号"""
        for idx, item in enumerate(self.tree.get_children(), start=1):
            values = self.tree.item(item)['values']
            if values:
                values[0] = idx
                self.tree.item(item, values=values)
    
    def update_count(self):
        """更新计数"""
        self.count_label.config(text=f"共 {len(self.batch_list)} 项")
    
    def start_batch(self):
        """开始批量下载"""
        if not self.batch_list:
            return
        
        download_format = self.format_var.get()
        
        # 更新状态
        for idx, item in enumerate(self.tree.get_children()):
            self.tree.item(item, values=(
                idx + 1,
                self.batch_list[idx],
                '下载中...'
            ))
        
        # 调用批量下载回调
        if self.batch_callback:
            self.batch_callback(self.batch_list, download_format, self.update_item_status)
    
    def update_item_status(self, url, status, success=True):
        """更新项目状态"""
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            if values and values[1] == url:
                if success:
                    self.tree.item(item, values=(values[0], values[1], '✓ 完成'))
                else:
                    self.tree.item(item, values=(values[0], values[1], '✗ 失败'))
                break
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)