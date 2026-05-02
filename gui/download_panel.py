import customtkinter as ctk
import threading
import time
from typing import Callable, Optional, Dict

from gui.styles import AppStyles


class DownloadPanel(ctk.CTkFrame):
    def __init__(self, parent, on_download_callback: Callable):
        super().__init__(parent, fg_color=AppStyles.COLORS['bg_dark'])
        self.on_download_callback = on_download_callback
        self.download_tasks: Dict[str, Dict] = {}
        self._setup_ui()

    def _setup_ui(self):
        title = AppStyles.create_label(self, text="📥 视频下载", font=AppStyles.FONTS['title'])
        title.pack(pady=(20, 10), padx=20, anchor='w')

        input_frame = AppStyles.create_card_frame(self)
        input_frame.pack(fill='x', padx=20, pady=10)

        url_label = AppStyles.create_label(input_frame, text="BV号 / 视频链接:")
        url_label.pack(pady=(15, 5), padx=15, anchor='w')

        self.url_entry = AppStyles.create_entry(
            input_frame,
            placeholder_text="输入BV号或完整链接，如: BV1xx4y1d7zc"
        )
        self.url_entry.pack(fill='x', padx=15, pady=(0, 10))
        self._setup_entry_shortcuts(self.url_entry)

        type_frame = ctk.CTkFrame(input_frame, fg_color='transparent')
        type_frame.pack(fill='x', padx=15, pady=(0, 15))

        type_label = AppStyles.create_label(type_frame, text="下载类型:")
        type_label.pack(side='left', padx=(0, 10))

        self.download_type = ctk.CTkOptionMenu(
            type_frame,
            values=["audio", "video", "all"],
            fg_color=AppStyles.COLORS['bg_light'],
            button_color=AppStyles.COLORS['accent'],
            text_color=AppStyles.COLORS['text_primary'],
            dropdown_fg_color=AppStyles.COLORS['bg_medium']
        )
        self.download_type.set("audio")
        self.download_type.pack(side='left')

        hint_label = ctk.CTkLabel(
            type_frame,
            text="audio=仅音频 | video=仅视频 | all=完整视频",
            text_color=AppStyles.COLORS['text_secondary'],
            font=AppStyles.FONTS['small']
        )
        hint_label.pack(side='left', padx=(20, 0))

        self.download_btn = AppStyles.create_button(
            input_frame,
            text="开始下载",
            command=self._start_download
        )
        self.download_btn.pack(fill='x', padx=15, pady=(0, 15))

        self.url_entry.bind('<Return>', lambda e: self._start_download())

        self.task_list_frame = AppStyles.create_card_frame(self)
        self.task_list_frame.pack(fill='both', expand=True, padx=20, pady=10)

        task_title = AppStyles.create_label(self.task_list_frame, text="下载队列", font=AppStyles.FONTS['heading'])
        task_title.pack(pady=(10, 5), padx=15, anchor='w')

        self.task_scroll = ctk.CTkScrollableFrame(
            self.task_list_frame,
            fg_color='transparent'
        )
        self.task_scroll.pack(fill='both', expand=True, padx=10, pady=5)

        self.empty_tip = AppStyles.create_label(
            self.task_scroll,
            text="输入BV号或链接开始下载",
            text_color=AppStyles.COLORS['text_secondary']
        )
        self.empty_tip.pack(pady=20)

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

    def _start_download(self):
        url_or_bvid = self.url_entry.get().strip()
        if not url_or_bvid:
            return

        download_type = self.download_type.get()
        task_id = f"task_{int(time.time() * 1000)}"

        if self.empty_tip.winfo_exists():
            self.empty_tip.pack_forget()

        self._add_task_to_queue(task_id, url_or_bvid)

        def download_task():
            try:
                if self.on_download_callback:
                    self.on_download_callback(
                        url_or_bvid,
                        download_type,
                        lambda tid, prog, status: self._update_task_progress(tid, prog, status)
                    )
                self._update_task_progress(task_id, 100, "下载完成")
            except Exception as e:
                self._update_task_progress(task_id, 0, f"错误: {str(e)}")

        thread = threading.Thread(target=download_task, daemon=True)
        thread.start()

    def _add_task_to_queue(self, task_id: str, video_name: str):
        task_frame = ctk.CTkFrame(self.task_scroll, fg_color=AppStyles.COLORS['bg_light'])
        task_frame.pack(fill='x', pady=5, padx=5)

        info_frame = ctk.CTkFrame(task_frame, fg_color='transparent')
        info_frame.pack(fill='x', padx=10, pady=5)

        name_label = ctk.CTkLabel(
            info_frame,
            text=video_name[:50] + "..." if len(video_name) > 50 else video_name,
            text_color=AppStyles.COLORS['text_primary'],
            font=AppStyles.FONTS['normal'],
            anchor='w'
        )
        name_label.pack(anchor='w')

        progress_frame = ctk.CTkFrame(task_frame, fg_color='transparent')
        progress_frame.pack(fill='x', padx=10)

        progress_bar = ctk.CTkProgressBar(progress_frame, progress_color=AppStyles.COLORS['accent'])
        progress_bar.pack(side='left', fill='x', expand=True, padx=(0, 10))
        progress_bar.set(0)

        progress_label = ctk.CTkLabel(
            progress_frame,
            text="0%",
            text_color=AppStyles.COLORS['text_secondary'],
            font=AppStyles.FONTS['small'],
            width=40
        )
        progress_label.pack(side='right')

        status_label = ctk.CTkLabel(
            task_frame,
            text="等待中...",
            text_color=AppStyles.COLORS['accent'],
            font=AppStyles.FONTS['small']
        )
        status_label.pack(padx=10, pady=(0, 5), anchor='w')

        self.download_tasks[task_id] = {
            'frame': task_frame,
            'progress': progress_bar,
            'progress_label': progress_label,
            'status_label': status_label
        }

    def _update_task_progress(self, task_id: str, progress: float, status: str):
        if task_id not in self.download_tasks:
            return

        def update():
            self.download_tasks[task_id]['progress'].set(progress / 100.0)
            self.download_tasks[task_id]['progress_label'].configure(text=f"{int(progress)}%")

            if progress >= 100:
                color = AppStyles.COLORS['success']
            elif '错误' in status or '失败' in status:
                color = AppStyles.COLORS['error']
            else:
                color = AppStyles.COLORS['accent']

            self.download_tasks[task_id]['status_label'].configure(text=status, text_color=color)

        self.after(0, update)

    def add_download_task(self, task_id: str, video_name: str, progress: float = 0, status: str = "等待中..."):
        if task_id in self.download_tasks:
            self._update_task_progress(task_id, progress, status)
            return

        if self.empty_tip.winfo_exists():
            self.empty_tip.pack_forget()

        self._add_task_to_queue(task_id, video_name)
        self._update_task_progress(task_id, progress, status)
