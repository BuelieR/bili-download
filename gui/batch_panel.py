import customtkinter as ctk
import threading
from typing import Callable, List
from pathlib import Path

from gui.styles import AppStyles


class BatchPanel(ctk.CTkFrame):
    def __init__(self, parent, on_download_callback: Callable):
        super().__init__(parent, fg_color=AppStyles.COLORS['bg_dark'])
        self.on_download_callback = on_download_callback
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
        self._setup_textbox_shortcuts()

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

        self.paste_btn = AppStyles.create_button(
            btn_row,
            text="粘贴",
            fg_color=AppStyles.COLORS['bg_light'],
            hover_color=AppStyles.COLORS['accent'],
            width=60,
            command=self._paste_text
        )
        self.paste_btn.pack(side='right')

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

        self.count_label = ctk.CTkLabel(
            settings_row,
            text="0 个视频",
            text_color=AppStyles.COLORS['text_secondary'],
            font=AppStyles.FONTS['small']
        )
        self.count_label.pack(side='left')

        self.start_btn = AppStyles.create_button(
            input_frame,
            text="开始批量下载",
            fg_color=AppStyles.COLORS['success'],
            hover_color='#45a049',
            command=self._start_batch_download
        )
        self.start_btn.pack(fill='x', padx=15, pady=(0, 15))

        self.textbox.bind('<KeyRelease>', lambda e: self._update_bvid_list())

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

    def _setup_textbox_shortcuts(self):
        self.textbox.bind('<Control-a>', self._select_all)
        self.textbox.bind('<Control-A>', self._select_all)
        self.textbox.bind('<Control-c>', self._copy_text)
        self.textbox.bind('<Control-C>', self._copy_text)
        self.textbox.bind('<Control-x>', self._cut_text)
        self.textbox.bind('<Control-X>', self._cut_text)
        self.textbox.bind('<Control-v>', self._paste_text)
        self.textbox.bind('<Control-V>', self._paste_text)

    def _select_all(self, event):
        self.textbox.tag_add('sel', '1.0', 'end')
        return 'break'

    def _copy_text(self, event):
        self.textbox.event_generate('<<Copy>>')
        return 'break'

    def _cut_text(self, event):
        self.textbox.event_generate('<<Cut>>')
        return 'break'

    def _paste_text(self, event=None):
        self.textbox.event_generate('<<Paste>>')
        self._update_bvid_list()
        return 'break'

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
        count = len(self.bvid_list)
        self.count_label.configure(text=f"{count} 个视频")
        if self.bvid_list:
            self.total_label.configure(
                text=f"共 {count} 个视频",
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

        for bvid in self.bvid_list:
            self._add_status_item(bvid, "等待中...")

        def batch_task():
            for bvid in self.bvid_list:
                self._update_status_item(bvid, "下载中...")

                def download_one(bvid=bvid):
                    try:
                        if self.on_download_callback:
                            def status_callback(task_id, progress, status):
                                self.after(0, lambda s=status: self._update_status_item(bvid, s))

                            self.on_download_callback(bvid, self.download_type.get(), status_callback)
                    except Exception as e:
                        self.after(0, lambda bv=bvid, err=str(e): self._update_status_item(bv, f"失败: {err}"))

                thread = threading.Thread(target=download_one, daemon=True)
                thread.start()

            self.after(0, lambda: self.total_label.configure(text=f"批量下载完成"))

        thread = threading.Thread(target=batch_task, daemon=True)
        thread.start()

    def _add_status_item(self, bvid: str, status: str):
        item_frame = ctk.CTkFrame(self.status_scroll, fg_color=AppStyles.COLORS['bg_light'])
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
            text=status,
            text_color=AppStyles.COLORS['text_secondary'],
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
