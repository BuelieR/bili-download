import customtkinter as ctk
import asyncio
import threading
from typing import Callable, Optional

from gui.styles import AppStyles
from gui.download_panel import DownloadPanel
from gui.search_panel import SearchPanel
from gui.batch_panel import BatchPanel
from gui.settings_panel import SettingsPanel


class MainWindow(ctk.CTk):
    def __init__(self, config, api, downloader):
        super().__init__()

        self.config = config
        self.api = api
        self.downloader = downloader

        self.title("B站下载器 v2.0 (GUI)")
        self.geometry("1000x700")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._setup_ui()
        self._setup_menu()

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_ui(self):
        self.tabview = ctk.CTkTabview(self, fg_color=AppStyles.COLORS['bg_dark'])
        self.tabview.pack(fill='both', expand=True, padx=10, pady=10)

        self.download_panel = DownloadPanel(self.tabview.add("📥 下载"), self._on_download)
        self.download_panel.pack(fill='both', expand=True)

        self.search_panel = SearchPanel(self.tabview.add("🔍 搜索"), self._on_search, self._on_download)
        self.search_panel.pack(fill='both', expand=True)

        self.batch_panel = BatchPanel(self.tabview.add("📋 批量"), self._on_batch_download)
        self.batch_panel.pack(fill='both', expand=True)

        self.settings_panel = SettingsPanel(self.tabview.add("⚙️ 设置"), self.config, self._on_settings_changed)
        self.settings_panel.pack(fill='both', expand=True)

    def _setup_menu(self):
        menubar = ctk.CTkFrame(self)
        menubar.configure(fg_color=AppStyles.COLORS['bg_medium'])

    def _on_download(self, url_or_bvid: str, download_type: str, progress_callback: Optional[Callable]):
        def download_task():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.downloader.download_video(url_or_bvid, download_type)
                )
                loop.close()

                if progress_callback and result:
                    progress_callback("", 100, "下载完成")
                elif progress_callback:
                    progress_callback("", 0, "下载失败")

            except Exception as e:
                if progress_callback:
                    progress_callback("", 0, f"错误: {str(e)}")

        thread = threading.Thread(target=download_task, daemon=True)
        thread.start()

    def _on_search(self, keyword: str):
        try:
            results = self.api.search_videos(keyword)
            return results
        except Exception as e:
            return []

    def _on_batch_download(self, url_list, download_type: str, status_callback: Optional[Callable]):
        for url in url_list:
            def download_one():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(
                        self.downloader.download_video(url, download_type)
                    )
                    loop.close()

                    if status_callback:
                        status_callback(url, "完成", True)
                except Exception as e:
                    if status_callback:
                        status_callback(url, f"失败: {str(e)}", False)

            thread = threading.Thread(target=download_one, daemon=True)
            thread.start()

    def _on_settings_changed(self, config):
        self.config = config

    def _on_closing(self):
        from tkinter import messagebox
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.destroy()

    def run(self):
        self.mainloop()
