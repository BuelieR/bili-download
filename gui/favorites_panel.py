import customtkinter as ctk
import threading
from typing import Callable, List, Dict

from gui.styles import AppStyles


class FavoritesPanel(ctk.CTkFrame):
    def __init__(self, parent, config, on_download_callback: Callable):
        super().__init__(parent, fg_color=AppStyles.COLORS['bg_dark'])
        self.config = config
        self.on_download_callback = on_download_callback
        self.favorites_list = []
        self._setup_ui()

    def _setup_ui(self):
        title = AppStyles.create_label(self, text="⭐ 收藏夹下载", font=AppStyles.FONTS['title'])
        title.pack(pady=(20, 10), padx=20, anchor='w')

        type_frame = ctk.CTkFrame(self, fg_color='transparent')
        type_frame.pack(fill='x', padx=20, pady=(0, 10))

        self.type_var = ctk.StringVar(value="public")

        public_radio = ctk.CTkRadioButton(
            type_frame,
            text="公开收藏夹",
            variable=self.type_var,
            value="public",
            text_color=AppStyles.COLORS['text_primary'],
            fg_color=AppStyles.COLORS['accent']
        )
        public_radio.pack(side='left', padx=(0, 20))

        private_radio = ctk.CTkRadioButton(
            type_frame,
            text="私密收藏夹",
            variable=self.type_var,
            value="private",
            text_color=AppStyles.COLORS['text_primary'],
            fg_color=AppStyles.COLORS['accent']
        )
        private_radio.pack(side='left')

        input_frame = AppStyles.create_card_frame(self)
        input_frame.pack(fill='x', padx=20, pady=10)

        fid_label = AppStyles.create_label(input_frame, text="收藏夹ID (media_id):")
        fid_label.pack(pady=(15, 5), padx=15, anchor='w')

        self.fid_entry = AppStyles.create_entry(
            input_frame,
            placeholder_text="输入收藏夹ID"
        )
        self.fid_entry.pack(fill='x', padx=15, pady=(0, 10))
        self._setup_entry_shortcuts(self.fid_entry)

        cookie_hint = ctk.CTkLabel(
            input_frame,
            text="私密收藏夹需要先在设置中配置SESSDATA",
            text_color=AppStyles.COLORS['text_secondary'],
            font=AppStyles.FONTS['small']
        )
        cookie_hint.pack(pady=(0, 10), padx=15, anchor='w')

        settings_row = ctk.CTkFrame(input_frame, fg_color='transparent')
        settings_row.pack(fill='x', padx=15, pady=(0, 10))

        type_label = AppStyles.create_label(settings_row, text="下载类型:")
        type_label.pack(side='left', padx=(0, 10))

        self.download_type = ctk.CTkOptionMenu(
            settings_row,
            values=["audio", "video", "all"],
            fg_color=AppStyles.COLORS['bg_light'],
            button_color=AppStyles.COLORS['accent'],
            text_color=AppStyles.COLORS['text_primary'],
            dropdown_fg_color=AppStyles.COLORS['bg_medium']
        )
        self.download_type.set("audio")
        self.download_type.pack(side='left')

        btn_frame = ctk.CTkFrame(input_frame, fg_color='transparent')
        btn_frame.pack(fill='x', padx=15, pady=(0, 15))

        self.fetch_btn = AppStyles.create_button(
            btn_frame,
            text="获取视频列表",
            command=self._fetch_favorites
        )
        self.fetch_btn.pack(side='left', padx=(0, 10))

        self.download_all_btn = AppStyles.create_button(
            btn_frame,
            text="下载全部",
            fg_color=AppStyles.COLORS['success'],
            hover_color='#45a049',
            command=self._download_all
        )
        self.download_all_btn.pack(side='left')
        self.download_all_btn.configure(state='disabled')

        self.results_frame = AppStyles.create_card_frame(self)
        self.results_frame.pack(fill='both', expand=True, padx=20, pady=10)

        results_title = AppStyles.create_label(
            self.results_frame,
            text="收藏夹内容",
            font=AppStyles.FONTS['heading']
        )
        results_title.pack(pady=(10, 5), padx=15, anchor='w')

        self.results_scroll = ctk.CTkScrollableFrame(
            self.results_frame,
            fg_color='transparent'
        )
        self.results_scroll.pack(fill='both', expand=True, padx=10, pady=5)

        self.status_label = AppStyles.create_label(
            self.results_scroll,
            text="输入收藏夹ID并获取列表",
            text_color=AppStyles.COLORS['text_secondary']
        )
        self.status_label.pack(pady=20)

        self.selected_count = AppStyles.create_label(
            self.results_frame,
            text="",
            text_color=AppStyles.COLORS['text_secondary'],
            font=AppStyles.FONTS['small']
        )
        self.selected_count.pack(pady=(0, 10), padx=15, anchor='e')

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

    def _fetch_favorites(self):
        fid = self.fid_entry.get().strip()
        if not fid.isdigit():
            return

        is_private = self.type_var.get() == 'private'

        cookie = self.config.get('cookie')
        if is_private and not cookie:
            from tkinter import messagebox
            messagebox.showwarning("提示", "私密收藏夹需要先配置SESSDATA")
            return

        self.fetch_btn.configure(state='disabled', text='获取中...')
        self.status_label.configure(text='获取中...')

        def fetch_task():
            try:
                from api.bili_api import BiliAPI
                api = BiliAPI(cookie if is_private else None)
                items = api.get_favorites(int(fid), is_private)
                self.after(0, lambda: self._display_results(items))
            except Exception as e:
                self.after(0, lambda: self._display_results([], str(e)))

        thread = threading.Thread(target=fetch_task, daemon=True)
        thread.start()

    def _display_results(self, results: List[Dict], error: str = None):
        self.fetch_btn.configure(state='normal', text='获取视频列表')

        for widget in self.results_scroll.winfo_children():
            widget.destroy()

        if error:
            self.status_label.configure(text=f"获取失败: {error}", text_color=AppStyles.COLORS['error'])
            self.status_label.pack(pady=20)
            self.download_all_btn.configure(state='disabled')
            return

        if not results:
            self.status_label.configure(text='未找到视频', text_color=AppStyles.COLORS['text_secondary'])
            self.status_label.pack(pady=20)
            self.download_all_btn.configure(state='disabled')
            return

        self.favorites_list = results
        self.status_label.pack_forget()

        for i, item in enumerate(results):
            self._create_result_item(item, i)

        self.download_all_btn.configure(state='normal')
        self.selected_count.configure(text=f"共 {len(results)} 个视频")

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
            text=f"👤 {item.get('author', '未知')}  |  BV号: {item.get('bvid', '')}",
            text_color=AppStyles.COLORS['text_secondary'],
            font=AppStyles.FONTS['small'],
            anchor='w'
        )
        meta_label.pack(anchor='w')

    def _download_all(self):
        selected_indices = []
        for widget in self.results_scroll.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, ctk.CTkCheckBox):
                    if child.get() != -1:
                        selected_indices.append(child.get())

        bvids = []
        for idx in selected_indices:
            if 0 <= idx < len(self.favorites_list):
                bvid = self.favorites_list[idx].get('bvid')
                if bvid:
                    bvids.append(bvid)

        if not bvids:
            return

        self._show_download_status(bvids)

        download_type = self.download_type.get()
        
        def download_one(bvid):
            def status_callback(task_id, progress, status):
                self.after(0, lambda: self._update_status_item(bvid, status))
            
            if self.on_download_callback:
                self.on_download_callback(bvid, download_type, status_callback)

        for bvid in bvids:
            thread = threading.Thread(target=download_one, args=(bvid,), daemon=True)
            thread.start()

    def _show_download_status(self, bvids: List[str]):
        for widget in self.results_scroll.winfo_children():
            widget.destroy()

        self.status_label.configure(text=f"正在下载 {len(bvids)} 个视频...", text_color=AppStyles.COLORS['text_primary'])
        self.status_label.pack(pady=10)

        for bvid in bvids:
            item_frame = ctk.CTkFrame(self.results_scroll, fg_color=AppStyles.COLORS['bg_light'])
            item_frame.pack(fill='x', pady=2)

            bvid_label = ctk.CTkLabel(
                item_frame,
                text=bvid,
                text_color=AppStyles.COLORS['text_primary'],
                font=AppStyles.FONTS['mono'],
                anchor='w'
            )
            bvid_label.pack(side='left', padx=10)

            status_label = ctk.CTkLabel(
                item_frame,
                text="下载中...",
                text_color=AppStyles.COLORS['accent'],
                font=AppStyles.FONTS['small'],
                width=80
            )
            status_label.pack(side='right', padx=10)
            item_frame.bvid = bvid
            item_frame.status_label = status_label

    def _update_status_item(self, bvid: str, status: str):
        for widget in self.results_scroll.winfo_children():
            if hasattr(widget, 'bvid') and widget.bvid == bvid:
                color = AppStyles.COLORS['success'] if '完成' in status else AppStyles.COLORS['error'] if '失败' in status else AppStyles.COLORS['accent']
                widget.status_label.configure(text=status, text_color=color)
                break
