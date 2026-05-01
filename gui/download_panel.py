import customtkinter as ctk
import threading
import time
from typing import Callable, Optional

from gui.styles import AppStyles


class DownloadPanel(ctk.CTkFrame):
    def __init__(self, parent, on_download_callback: Callable):
        super().__init__(parent, fg_color=AppStyles.COLORS['bg_dark'])
        self.on_download_callback = on_download_callback
        self.download_tasks = {}
        self._setup_ui()

    def _setup_ui(self):
        title = AppStyles.create_label(self, text="📥 视频下载", font=AppStyles.FONTS['title'])
        title.pack(pady=(20, 10), padx=20, anchor='w')

        input_frame = AppStyles.create_card_frame(self)
        input_frame.pack(fill='x', padx=20, pady=10)

        url_label = AppStyles.create_label(input_frame, text="BV号 / 视频链接:")
        url_label.pack(pady=(15, 5), padx=15, anchor='w')

        self.url_entry = AppStyles.create_entry(input_frame, placeholder_text="输入BV号或完整链接，如: BV1xx4y1d7zc")
        self.url_entry.pack(fill='x', padx=15, pady=(0, 10))

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

        self.download_btn = AppStyles.create_button(
            input_frame,
            text="开始下载",
            command=self._start_download
        )
        self.download_btn.pack(fill='x', padx=15, pady=(0, 15))

        self.task_list_frame = AppStyles.create_card_frame(self)
        self.task_list_frame.pack(fill='both', expand=True, padx=20, pady=10)

        task_title = AppStyles.create_label(self.task_list_frame, text="下载队列", font=AppStyles.FONTS['heading'])
        task_title.pack(pady=(10, 5), padx=15, anchor='w')

        self.task_scroll = ctk.CTkScrollableFrame(
            self.task_list_frame,
            fg_color='transparent'
        )
        self.task_scroll.pack(fill='both', expand=True, padx=10, pady=5)
    
    def _setup_shortcuts(self):
        self.url_entry.bind('<Control-a>', self._select_all)
        self.url_entry.bind('<Control-A>', self._select_all)
        self.url_entry.bind('<Control-c>', self._copy_text)
        self.url_entry.bind('<Control-C>', self._copy_text)
        self.url_entry.bind('<Control-x>', self._cut_text)
        self.url_entry.bind('<Control-X>', self._cut_text)
        self.url_entry.bind('<Control-v>', self._paste_text)
        self.url_entry.bind('<Control-V>', self._paste_text)
    
    def _select_all(self, event):
        self.url_entry.select_range(0, 'end')
        return 'break'
    
    def _copy_text(self, event):
        self.url_entry.event_generate('<<Copy>>')
        return 'break'
    
    def _cut_text(self, event):
        self.url_entry.event_generate('<<Cut>>')
        return 'break'
    
    def _paste_text(self, event):
        self.url_entry.event_generate('<<Paste>>')
        return 'break'

    def _start_download(self):
        url_or_bvid = self.url_entry.get().strip()
        if not url_or_bvid:
            return

        download_type = self.download_type.get()
        task_id = f"task_{int(time.time() * 1000)}"

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
        task_frame.pack(fill='x', pady=5)

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

        self.download_tasks[task_id] = {
            'frame': task_frame,
            'progress': ctk.CTkProgressBar(task_frame, progress_color=AppStyles.COLORS['accent']),
            'status_label': None
        }
        self.download_tasks[task_id]['progress'].pack(fill='x', padx=10, pady=(0, 5))
        self.download_tasks[task_id]['progress'].set(0)

    def _update_task_progress(self, task_id: str, progress: float, status: str):
        if task_id not in self.download_tasks:
            return

        def update():
            self.download_tasks[task_id]['progress'].set(progress / 100.0)
            if self.download_tasks[task_id]['status_label']:
                self.download_tasks[task_id]['status_label'].destroy()

            color = AppStyles.COLORS['success'] if progress >= 100 else AppStyles.COLORS['accent']
            status_label = ctk.CTkLabel(
                self.download_tasks[task_id]['frame'],
                text=status,
                text_color=color,
                font=AppStyles.FONTS['small']
            )
            status_label.pack(pady=(0, 5))
            self.download_tasks[task_id]['status_label'] = status_label

        self.after(0, update)
