import customtkinter as ctk
from typing import Callable, List, Dict
from datetime import datetime
import json
from pathlib import Path


class HistoryPanel(ctk.CTkFrame):
    def __init__(self, parent, on_re_download_callback: Callable):
        super().__init__(parent, fg_color=AppStyles.COLORS['bg_dark'])
        self.on_re_download_callback = on_re_download_callback
        self.history = []
        self._setup_ui()

    def _setup_ui(self):
        from gui.styles import AppStyles

        title = AppStyles.create_label(self, text="📜 下载历史", font=AppStyles.FONTS['title'])
        title.pack(pady=(20, 10), padx=20, anchor='w')

        btn_frame = ctk.CTkFrame(self, fg_color='transparent')
        btn_frame.pack(fill='x', padx=20, pady=(0, 10))

        self.clear_btn = AppStyles.create_button(
            btn_frame,
            text="清空历史",
            fg_color=AppStyles.COLORS['warning'],
            hover_color='#e68a00',
            width=100,
            command=self._clear_history
        )
        self.clear_btn.pack(side='right')

        self.filter_var = ctk.StringVar(value="all")
        filter_frame = ctk.CTkFrame(btn_frame, fg_color='transparent')
        filter_frame.pack(side='left')

        all_radio = ctk.CTkRadioButton(
            filter_frame,
            text="全部",
            variable=self.filter_var,
            value="all",
            text_color=AppStyles.COLORS['text_primary'],
            fg_color=AppStyles.COLORS['accent'],
            command=self._filter_history
        )
        all_radio.pack(side='left', padx=(0, 15))

        success_radio = ctk.CTkRadioButton(
            filter_frame,
            text="成功",
            variable=self.filter_var,
            value="success",
            text_color=AppStyles.COLORS['text_primary'],
            fg_color=AppStyles.COLORS['success'],
            command=self._filter_history
        )
        success_radio.pack(side='left', padx=(0, 15))

        failed_radio = ctk.CTkRadioButton(
            filter_frame,
            text="失败",
            variable=self.filter_var,
            value="failed",
            text_color=AppStyles.COLORS['text_primary'],
            fg_color=AppStyles.COLORS['error'],
            command=self._filter_history
        )
        failed_radio.pack(side='left')

        self.history_frame = AppStyles.create_card_frame(self)
        self.history_frame.pack(fill='both', expand=True, padx=20, pady=10)

        history_title = AppStyles.create_label(
            self.history_frame,
            text="下载记录",
            font=AppStyles.FONTS['heading']
        )
        history_title.pack(pady=(10, 5), padx=15, anchor='w')

        self.stats_label = AppStyles.create_label(
            self.history_frame,
            text="",
            text_color=AppStyles.COLORS['text_secondary'],
            font=AppStyles.FONTS['small']
        )
        self.stats_label.pack(pady=(0, 5), padx=15, anchor='e')

        self.history_scroll = ctk.CTkScrollableFrame(
            self.history_frame,
            fg_color='transparent'
        )
        self.history_scroll.pack(fill='both', expand=True, padx=10, pady=5)

        self.empty_label = AppStyles.create_label(
            self.history_scroll,
            text="暂无下载记录",
            text_color=AppStyles.COLORS['text_secondary']
        )
        self.empty_label.pack(pady=20)

    def _load_history(self):
        history_path = Path(__file__).parent.parent / "download_history.json"
        if history_path.exists():
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        self._display_history()

    def _save_history(self):
        history_path = Path(__file__).parent.parent / "download_history.json"
        try:
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except:
            pass

    def add_download(self, bvid: str, download_type: str, status: str):
        record = {
            'bvid': bvid,
            'type': download_type,
            'status': status,
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'title': ""
        }
        self.history.insert(0, record)
        if len(self.history) > 100:
            self.history = self.history[:100]
        self._save_history()
        if hasattr(self, '_loaded'):
            self._display_history()

    def _filter_history(self):
        self._display_history()

    def _get_filtered_history(self) -> List[Dict]:
        filter_type = self.filter_var.get()
        if filter_type == 'all':
            return self.history
        return [h for h in self.history if h.get('status') == filter_type]

    def _display_history(self):
        from gui.styles import AppStyles

        for widget in self.history_scroll.winfo_children():
            if widget != self.empty_label:
                widget.destroy()

        filtered_history = self._get_filtered_history()

        success_count = sum(1 for h in self.history if h.get('status') == 'success')
        failed_count = sum(1 for h in self.history if h.get('status') == 'failed')
        self.stats_label.configure(text=f"成功: {success_count} | 失败: {failed_count}")

        if not filtered_history:
            if not self.empty_label.winfo_ismapped():
                self.empty_label.pack(pady=20)
            return

        if self.empty_label.winfo_ismapped():
            self.empty_label.pack_forget()

        for record in filtered_history:
            self._create_history_item(record)

    def _create_history_item(self, record: Dict):
        from gui.styles import AppStyles

        item_frame = ctk.CTkFrame(self.history_scroll, fg_color=AppStyles.COLORS['bg_light'])
        item_frame.pack(fill='x', pady=3, padx=5)

        info_frame = ctk.CTkFrame(item_frame, fg_color='transparent')
        info_frame.pack(side='left', fill='both', expand=True, padx=10, pady=8)

        bvid_label = ctk.CTkLabel(
            info_frame,
            text=f"BV号: {record.get('bvid', '')}",
            text_color=AppStyles.COLORS['text_primary'],
            font=AppStyles.FONTS['mono'],
            anchor='w'
        )
        bvid_label.pack(anchor='w')

        meta_label = ctk.CTkLabel(
            info_frame,
            text=f"类型: {record.get('type', '')} | {record.get('time', '')}",
            text_color=AppStyles.COLORS['text_secondary'],
            font=AppStyles.FONTS['small'],
            anchor='w'
        )
        meta_label.pack(anchor='w')

        status_frame = ctk.CTkFrame(item_frame, fg_color='transparent')
        status_frame.pack(side='right', padx=10)

        status_color = AppStyles.COLORS['success'] if record.get('status') == 'success' else AppStyles.COLORS['error']
        status_text = "成功" if record.get('status') == 'success' else "失败"
        status_label = ctk.CTkLabel(
            status_frame,
            text=status_text,
            text_color=status_color,
            font=AppStyles.FONTS['heading'],
            width=40
        )
        status_label.pack(anchor='e', pady=(0, 5))

        retry_btn = ctk.CTkButton(
            status_frame,
            text="重新下载",
            fg_color=AppStyles.COLORS['bg_card'],
            hover_color=AppStyles.COLORS['accent'],
            text_color=AppStyles.COLORS['text_primary'],
            corner_radius=4,
            height=24,
            width=70,
            font=AppStyles.FONTS['small'],
            command=lambda bvid=record.get('bvid'), dtype=record.get('type'): self._re_download(bvid, dtype)
        )
        retry_btn.pack(anchor='e')

    def _re_download(self, bvid: str, download_type: str):
        if self.on_re_download_callback and bvid:
            self.on_re_download_callback(bvid, download_type)

    def _clear_history(self):
        from tkinter import messagebox
        if messagebox.askyesno("确认", "确定要清空所有下载历史吗？"):
            self.history = []
            self._save_history()
            self._display_history()


from gui.styles import AppStyles