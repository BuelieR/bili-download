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
        self.current_page = 1
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
        self._setup_entry_shortcuts(self.search_entry)

        btn_frame = ctk.CTkFrame(search_frame, fg_color='transparent')
        btn_frame.pack(fill='x', padx=15, pady=(0, 15))

        self.search_btn = AppStyles.create_button(
            btn_frame,
            text="搜索",
            command=self._do_search
        )
        self.search_btn.pack(side='left', padx=(0, 10))

        type_label = AppStyles.create_label(btn_frame, text="下载类型:")
        type_label.pack(side='left', padx=(20, 10))

        self.download_type = ctk.CTkOptionMenu(
            btn_frame,
            values=["audio", "video", "all"],
            fg_color=AppStyles.COLORS['bg_light'],
            button_color=AppStyles.COLORS['accent'],
            text_color=AppStyles.COLORS['text_primary'],
            dropdown_fg_color=AppStyles.COLORS['bg_medium']
        )
        self.download_type.set("audio")
        self.download_type.pack(side='left')

        self.download_selected_btn = AppStyles.create_button(
            btn_frame,
            text="下载选中",
            fg_color=AppStyles.COLORS['success'],
            hover_color='#45a049',
            command=self._download_selected
        )
        self.download_selected_btn.pack(side='right')
        self.download_selected_btn.configure(state='disabled')

        self.search_entry.bind('<Return>', lambda e: self._do_search())

        self.results_frame = AppStyles.create_card_frame(self)
        self.results_frame.pack(fill='both', expand=True, padx=20, pady=10)

        results_header = ctk.CTkFrame(self.results_frame, fg_color='transparent')
        results_header.pack(fill='x', padx=15, pady=(10, 5))

        results_title = AppStyles.create_label(results_header, text="搜索结果", font=AppStyles.FONTS['heading'])
        results_title.pack(side='left')

        self.page_label = AppStyles.create_label(
            results_header,
            text="第 1 页",
            text_color=AppStyles.COLORS['text_secondary'],
            font=AppStyles.FONTS['small']
        )
        self.page_label.pack(side='right')

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

        self.page_control = ctk.CTkFrame(self.results_frame, fg_color='transparent')
        self.page_control.pack(fill='x', padx=15, pady=(0, 10))

        self.prev_btn = AppStyles.create_button(
            self.page_control,
            text="上一页",
            fg_color=AppStyles.COLORS['bg_light'],
            hover_color=AppStyles.COLORS['accent'],
            text_color=AppStyles.COLORS['text_primary'],
            width=80,
            command=self._prev_page
        )
        self.prev_btn.pack(side='left')
        self.prev_btn.configure(state='disabled')

        self.next_btn = AppStyles.create_button(
            self.page_control,
            text="下一页",
            fg_color=AppStyles.COLORS['bg_light'],
            hover_color=AppStyles.COLORS['accent'],
            text_color=AppStyles.COLORS['text_primary'],
            width=80,
            command=self._next_page
        )
        self.next_btn.pack(side='right')
        self.next_btn.configure(state='disabled')

    def _setup_entry_shortcuts(self, entry):
        entry.bind('<Control-a>', self._select_all)
        entry.bind('<Control-A>', self._select_all)
        entry.bind('<Control-c>', self._copy_text)
        entry.bind('<Control-C>', self._copy_text)
        entry.bind('<Control-x>', self._cut_text)
        entry.bind('<Control-X>', self._cut_text)
        entry.bind('<Control-v>', self._paste_text)
        entry.bind('<Control-V>', self._paste_text)

    def _select_all(self, event):
        event.widget.select_range(0, 'end')
        return 'break'

    def _copy_text(self, event):
        event.widget.event_generate('<<Copy>>')
        return 'break'

    def _cut_text(self, event):
        event.widget.event_generate('<<Cut>>')
        return 'break'

    def _paste_text(self, event):
        event.widget.event_generate('<<Paste>>')
        return 'break'

    def _do_search(self, page: int = 1):
        keyword = self.search_entry.get().strip()
        if not keyword:
            return

        self.search_btn.configure(state='disabled', text='搜索中...')
        self.status_label.configure(text='搜索中...')

        def search_task():
            try:
                results = self.on_search_callback(keyword, page) if self.on_search_callback else []
                self.after(0, lambda: self._display_results(results, page))
            except Exception as e:
                self.after(0, lambda: self._display_results([], page, str(e)))

        thread = threading.Thread(target=search_task, daemon=True)
        thread.start()

    def _display_results(self, results: List[Dict], page: int, error: str = None):
        self.search_btn.configure(state='normal', text='搜索')

        for widget in self.results_scroll.winfo_children():
            widget.destroy()

        if error:
            self.status_label.configure(text=f"搜索失败: {error}", text_color=AppStyles.COLORS['error'])
            self.status_label.pack(pady=20)
            self.download_selected_btn.configure(state='disabled')
            self.prev_btn.configure(state='disabled')
            self.next_btn.configure(state='disabled')
            return

        if not results:
            self.status_label.configure(text='未找到结果', text_color=AppStyles.COLORS['text_secondary'])
            self.status_label.pack(pady=20)
            self.download_selected_btn.configure(state='disabled')
            self.prev_btn.configure(state='normal' if page > 1 else 'disabled')
            self.next_btn.configure(state='disabled')
            return

        self.search_results = results
        self.current_page = page
        self.page_label.configure(text=f"第 {page} 页")
        self.status_label.pack_forget()

        for i, item in enumerate(results):
            self._create_result_item(item, i)

        self.download_selected_btn.configure(state='normal')
        self.prev_btn.configure(state='normal' if page > 1 else 'disabled')
        self.next_btn.configure(state='normal')

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
            self.on_download_callback(bvid, self.download_type.get(), None)

    def _download_selected(self):
        selected_indices = []
        for widget in self.results_scroll.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, ctk.CTkCheckBox):
                    if child.get() != -1:
                        selected_indices.append(child.get())

        download_type = self.download_type.get()
        for idx in selected_indices:
            if 0 <= idx < len(self.search_results):
                item = self.search_results[idx]
                bvid = item.get('bvid')
                if bvid and self.on_download_callback:
                    self.on_download_callback(bvid, download_type, None)

    def _prev_page(self):
        if self.current_page > 1:
            self._do_search(self.current_page - 1)

    def _next_page(self):
        self._do_search(self.current_page + 1)
