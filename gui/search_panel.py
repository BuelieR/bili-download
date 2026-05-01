import customtkinter as ctk
import threading
from typing import Callable, List, Dict

from gui.styles import AppStyles


class SearchPanel(ctk.CTkFrame):
    def __init__(self, parent, on_search_callback: Callable, on_download_callback: Callable):
        super().__init__(parent, fg_color=AppStyles.COLORS['bg_dark'])
        self.on_search_callback = on_search_callback
        self.on_download_callback = on_download_callback
        self.search_results = []
        self._setup_ui()

    def _setup_ui(self):
        title = AppStyles.create_label(self, text="🔍 搜索视频", font=AppStyles.FONTS['title'])
        title.pack(pady=(20, 10), padx=20, anchor='w')

        search_frame = AppStyles.create_card_frame(self)
        search_frame.pack(fill='x', padx=20, pady=10)

        self.search_entry = AppStyles.create_entry(
            search_frame,
            placeholder_text="输入搜索关键词"
        )
        self.search_entry.pack(fill='x', padx=15, pady=15)

        btn_frame = ctk.CTkFrame(search_frame, fg_color='transparent')
        btn_frame.pack(fill='x', padx=15, pady=(0, 15))

        self.search_btn = AppStyles.create_button(
            btn_frame,
            text="搜索",
            command=self._do_search
        )
        self.search_btn.pack(side='left', padx=(0, 10))

        self.download_selected_btn = AppStyles.create_button(
            btn_frame,
            text="下载选中",
            fg_color=AppStyles.COLORS['success'],
            hover_color='#45a049',
            command=self._download_selected
        )
        self.download_selected_btn.pack(side='left')
        self.download_selected_btn.configure(state='disabled')

        self.results_frame = AppStyles.create_card_frame(self)
        self.results_frame.pack(fill='both', expand=True, padx=20, pady=10)

        results_title = AppStyles.create_label(self.results_frame, text="搜索结果", font=AppStyles.FONTS['heading'])
        results_title.pack(pady=(10, 5), padx=15, anchor='w')

        self.results_scroll = ctk.CTkScrollableFrame(
            self.results_frame,
            fg_color='transparent'
        )
        self.results_scroll.pack(fill='both', expand=True, padx=10, pady=5)

        self.status_label = AppStyles.create_label(
            self.results_scroll,
            text="输入关键词开始搜索",
            text_color=AppStyles.COLORS['text_secondary']
        )
        self.status_label.pack(pady=20)

    def _setup_shortcuts(self):
        self.search_entry.bind('<Control-a>', self._select_all)
        self.search_entry.bind('<Control-A>', self._select_all)
        self.search_entry.bind('<Control-c>', self._copy_text)
        self.search_entry.bind('<Control-C>', self._copy_text)
        self.search_entry.bind('<Control-x>', self._cut_text)
        self.search_entry.bind('<Control-X>', self._cut_text)
        self.search_entry.bind('<Control-v>', self._paste_text)
        self.search_entry.bind('<Control-V>', self._paste_text)
    
    def _select_all(self, event):
        self.search_entry.select_range(0, 'end')
        return 'break'
    
    def _copy_text(self, event):
        self.search_entry.event_generate('<<Copy>>')
        return 'break'
    
    def _cut_text(self, event):
        self.search_entry.event_generate('<<Cut>>')
        return 'break'
    
    def _paste_text(self, event):
        self.search_entry.event_generate('<<Paste>>')
        return 'break'
    
    def _do_search(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            return

        self.search_btn.configure(state='disabled', text='搜索中...')
        self.status_label.configure(text='搜索中...')

        def search_task():
            try:
                results = self.on_search_callback(keyword) if self.on_search_callback else []
                self.after(0, lambda: self._display_results(results))
            except Exception as e:
                self.after(0, lambda: self._display_results([], str(e)))

        thread = threading.Thread(target=search_task, daemon=True)
        thread.start()

    def _display_results(self, results: List[Dict], error: str = None):
        self.search_btn.configure(state='normal', text='搜索')

        for widget in self.results_scroll.winfo_children():
            if widget != self.status_label:
                widget.destroy()

        if error:
            self.status_label.configure(text=f"搜索失败: {error}", text_color=AppStyles.COLORS['error'])
            self.status_label.pack(pady=20)
            return

        if not results:
            self.status_label.configure(text='未找到结果', text_color=AppStyles.COLORS['text_secondary'])
            self.status_label.pack(pady=20)
            self.download_selected_btn.configure(state='disabled')
            return

        self.search_results = results
        self.status_label.pack_forget()

        for i, item in enumerate(results):
            self._create_result_item(item, i)

        self.download_selected_btn.configure(state='normal')

    def _create_result_item(self, item: Dict, index: int):
        item_frame = ctk.CTkFrame(self.results_scroll, fg_color=AppStyles.COLORS['bg_light'])
        item_frame.pack(fill='x', pady=3)

        checkbox = ctk.CTkCheckBox(
            item_frame,
            text="",
            onvalue=index,
            offvalue=-1,
            fg_color=AppStyles.COLORS['accent']
        )
        checkbox.select()
        checkbox.pack(side='left', padx=(10, 5))

        info_frame = ctk.CTkFrame(item_frame, fg_color='transparent')
        info_frame.pack(side='left', fill='both', expand=True, padx=5, pady=8)

        title_label = ctk.CTkLabel(
            info_frame,
            text=item.get('title', '未知标题'),
            text_color=AppStyles.COLORS['text_primary'],
            font=AppStyles.FONTS['normal'],
            anchor='w'
        )
        title_label.pack(anchor='w')

        meta_label = ctk.CTkLabel(
            info_frame,
            text=f"👤 {item.get('author', '未知')}  |  📺 {item.get('play', 0)}播放  |  ⏱ {item.get('duration', '')}",
            text_color=AppStyles.COLORS['text_secondary'],
            font=AppStyles.FONTS['small'],
            anchor='w'
        )
        meta_label.pack(anchor='w')

        bvid_label = ctk.CTkLabel(
            info_frame,
            text=f"BV号: {item.get('bvid', '')}",
            text_color=AppStyles.COLORS['text_disabled'],
            font=AppStyles.FONTS['small'],
            anchor='w'
        )
        bvid_label.pack(anchor='w')

        download_btn = ctk.CTkButton(
            item_frame,
            text="下载",
            fg_color=AppStyles.COLORS['success'],
            hover_color='#45a049',
            width=60,
            command=lambda bvid=item.get('bvid'): self._quick_download(bvid)
        )
        download_btn.pack(side='right', padx=10)

    def _quick_download(self, bvid: str):
        if self.on_download_callback:
            self.on_download_callback(bvid, "audio", None)

    def _download_selected(self):
        selected_indices = []
        for widget in self.results_scroll.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, ctk.CTkCheckBox):
                    if child.get() != -1:
                        selected_indices.append(child.get())

        for idx in selected_indices:
            if 0 <= idx < len(self.search_results):
                item = self.search_results[idx]
                bvid = item.get('bvid')
                if bvid and self.on_download_callback:
                    self.on_download_callback(bvid, "audio", None)
