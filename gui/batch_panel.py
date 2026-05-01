import customtkinter as ctk
import threading
from typing import Callable, List
from pathlib import Path

from gui.styles import AppStyles


class BatchPanel(ctk.CTkFrame):
    def __init__(self, parent, on_batch_download_callback: Callable):
        super().__init__(parent, fg_color=AppStyles.COLORS['bg_dark'])
        self.on_batch_download_callback = on_batch_download_callback
        self.bvid_list = []
        self._setup_ui()

    def _setup_ui(self):
        title = AppStyles.create_label(self, text="📋 批量下载", font=AppStyles.FONTS['title'])
        title.pack(pady=(20, 10), padx=20, anchor='w')

        input_frame = AppStyles.create_card_frame(self)
        input_frame.pack(fill='x', padx=20, pady=10)

        input_label = AppStyles.create_label(
            input_frame,
            text="输入多个BV号或链接 (每行一个):"
        )
        input_label.pack(pady=(15, 5), padx=15, anchor='w')

        self.textbox = AppStyles.create_textbox(
            input_frame,
            height=150,
            font=AppStyles.FONTS['mono']
        )
        self.textbox.pack(fill='x', padx=15, pady=(0, 10))

        btn_row = ctk.CTkFrame(input_frame, fg_color='transparent')
        btn_row.pack(fill='x', padx=15, pady=(0, 10))

        self.import_btn = AppStyles.create_button(
            btn_row,
            text="从文件导入",
            fg_color=AppStyles.COLORS['bg_light'],
            hover_color=AppStyles.COLORS['accent'],
            command=self._import_from_file
        )
        self.import_btn.pack(side='left', padx=(0, 10))

        self.clear_btn = AppStyles.create_button(
            btn_row,
            text="清空",
            fg_color=AppStyles.COLORS['bg_light'],
            hover_color=AppStyles.COLORS['warning'],
            command=self._clear_list
        )
        self.clear_btn.pack(side='left')

        settings_row = ctk.CTkFrame(input_frame, fg_color='transparent')
        settings_row.pack(fill='x', padx=15, pady=(0, 15))

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
        self.download_type.pack(side='left', padx=(0, 20))

        self.start_btn = AppStyles.create_button(
            input_frame,
            text="开始批量下载",
            fg_color=AppStyles.COLORS['success'],
            hover_color='#45a049',
            command=self._start_batch_download
        )
        self.start_btn.pack(fill='x', padx=15, pady=(0, 15))

        self.status_frame = AppStyles.create_card_frame(self)
        self.status_frame.pack(fill='both', expand=True, padx=20, pady=10)

        status_title = AppStyles.create_label(
            self.status_frame,
            text="下载状态",
            font=AppStyles.FONTS['heading']
        )
        status_title.pack(pady=(10, 5), padx=15, anchor='w')

        self.status_scroll = ctk.CTkScrollableFrame(
            self.status_frame,
            fg_color='transparent'
        )
        self.status_scroll.pack(fill='both', expand=True, padx=10, pady=5)

        self.total_label = AppStyles.create_label(
            self.status_scroll,
            text="等待添加任务...",
            text_color=AppStyles.COLORS['text_secondary']
        )
        self.total_label.pack(pady=10)

    def _parse_bvid_list(self) -> List[str]:
        content = self.textbox.get("0.0", "end").strip()
        lines = content.split('\n')
        bvids = []
        for line in lines:
            line = line.strip()
            if line:
                import re
                bv_match = re.search(r'BV[a-zA-Z0-9]{10}', line)
                if bv_match:
                    bvids.append(bv_match.group(0))
                elif re.match(r'^BV[a-zA-Z0-9]{10}$', line):
                    bvids.append(line)
        return bvids

    def _update_bvid_list(self):
        self.bvid_list = self._parse_bvid_list()
        if self.bvid_list:
            self.total_label.configure(
                text=f"共 {len(self.bvid_list)} 个视频",
                text_color=AppStyles.COLORS['text_primary']
            )
        else:
            self.total_label.configure(
                text="等待添加任务...",
                text_color=AppStyles.COLORS['text_secondary']
            )

    def _import_from_file(self):
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="选择TXT文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.textbox.delete("0.0", "end")
                self.textbox.insert("0.0", content)
                self._update_bvid_list()
            except Exception as e:
                pass

    def _clear_list(self):
        self.textbox.delete("0.0", "end")
        self._update_bvid_list()

    def _start_batch_download(self):
        self._update_bvid_list()
        if not self.bvid_list:
            return

        for widget in self.status_scroll.winfo_children():
            widget.destroy()

        self.total_label = ctk.CTkLabel(
            self.status_scroll,
            text=f"正在下载 {len(self.bvid_list)} 个视频...",
            text_color=AppStyles.COLORS['text_primary']
        )
        self.total_label.pack(pady=10)

        def batch_task():
            for i, bvid in enumerate(self.bvid_list):
                self.after(0, lambda idx=i, bv=bvid: self._add_status_item(idx, bv, "下载中..."))

                if self.on_batch_download_callback:
                    def status_callback(url, status, success):
                        self.after(0, lambda u=url, s=status: self._update_status_item(u, s))

                    try:
                        self.on_batch_download_callback([bvid], self.download_type.get(), status_callback)
                        self.after(0, lambda idx=i, bv=bvid: self._update_status_item(bv, "完成"))
                    except Exception as e:
                        self.after(0, lambda idx=i, bv=bvid, err=str(e): self._update_status_item(bv, f"失败: {err}"))

            self.after(0, lambda: self.total_label.configure(text=f"批量下载完成，共 {len(self.bvid_list)} 个视频"))

        thread = threading.Thread(target=batch_task, daemon=True)
        thread.start()

    def _add_status_item(self, index: int, bvid: str, status: str):
        item_frame = ctk.CTkFrame(self.status_scroll, fg_color=AppStyles.COLORS['bg_light'])
        item_frame.pack(fill='x', pady=2)

        idx_label = ctk.CTkLabel(
            item_frame,
            text=f"{index + 1}.",
            text_color=AppStyles.COLORS['text_secondary'],
            width=30,
            font=AppStyles.FONTS['mono']
        )
        idx_label.pack(side='left', padx=(10, 5))

        bvid_label = ctk.CTkLabel(
            item_frame,
            text=bvid,
            text_color=AppStyles.COLORS['text_primary'],
            font=AppStyles.FONTS['mono'],
            anchor='w'
        )
        bvid_label.pack(side='left', fill='x', expand=True)

        status_label = ctk.CTkLabel(
            item_frame,
            text=status,
            text_color=AppStyles.COLORS['accent'],
            font=AppStyles.FONTS['small'],
            width=80
        )
        status_label.pack(side='right', padx=10)
        item_frame.bvid = bvid
        item_frame.status_label = status_label

    def _update_status_item(self, bvid: str, status: str):
        for widget in self.status_scroll.winfo_children():
            if hasattr(widget, 'bvid') and widget.bvid == bvid:
                color = AppStyles.COLORS['success'] if '完成' in status else AppStyles.COLORS['error'] if '失败' in status else AppStyles.COLORS['accent']
                widget.status_label.configure(text=status, text_color=color)
                break
