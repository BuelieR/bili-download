import customtkinter as ctk
import asyncio
import threading
import time
from typing import Callable, Optional, Dict, List

from gui.styles import AppStyles
from gui.download_panel import DownloadPanel
from gui.search_panel import SearchPanel
from gui.batch_panel import BatchPanel
from gui.favorites_panel import FavoritesPanel
from gui.settings_panel import SettingsPanel
from gui.history_panel import HistoryPanel


class MainWindow(ctk.CTk):
    def __init__(self, config, api, downloader, version:str = "0.0.0"):
        super().__init__()

        self.config = config
        self.api = api
        self.downloader = downloader
        self.current_theme = 'dark'

        self.title("B站下载器")
        self.version = version
        self.geometry("1100x750")
        self.minsize(900, 600)

        ctk.set_appearance_mode(self.current_theme)
        ctk.set_default_color_theme("blue")

        self._setup_ui()
        self._setup_shortcuts()

        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(
            self,
            width=180,
            fg_color=AppStyles.COLORS['bg_medium'],
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky='nsew')
        self.sidebar.grid_propagate(False)

        self._create_sidebar()

        self.content_frame = ctk.CTkFrame(
            self,
            fg_color=AppStyles.COLORS['bg_dark']
        )
        self.content_frame.grid(row=0, column=1, sticky='nsew')
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.panels: Dict[str, ctk.CTkFrame] = {}
        self._create_panels()

        self._show_panel('download')

    def _create_sidebar(self):
        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color='transparent',
            height=80
        )
        logo_frame.pack(fill='x', pady=(20, 10))

        self.logo_label = AppStyles.create_label(
            logo_frame,
            text="📥 B站下载器",
            font=AppStyles.FONTS['heading']
        )
        self.logo_label.pack(pady=20, padx=20)

        self.nav_buttons = []

        nav_items = [
            ('download', '📥 下载'),
            ('search', '🔍 搜索'),
            ('batch', '📋 批量'),
            ('favorites', '⭐ 收藏夹'),
            ('history', '📜 历史'),
            ('settings', '⚙️ 设置')
        ]

        for panel_id, text in nav_items:
            btn = AppStyles.create_sidebar_button(
                self.sidebar,
                text=text,
                command=lambda id=panel_id: self._show_panel(id)
            )
            btn.pack(fill='x', padx=8)
            self.nav_buttons.append((panel_id, btn))

        self.sidebar_separator = ctk.CTkFrame(
            self.sidebar,
            height=1,
            fg_color=AppStyles.COLORS['border']
        )
        self.sidebar_separator.pack(fill='x', pady=(10, 5), padx=15)

        self.theme_switch = ctk.CTkSwitch(
            self.sidebar,
            text="浅色模式",
            text_color=AppStyles.COLORS['text_secondary'],
            command=self._toggle_theme
        )
        self.theme_switch.pack(pady=10, padx=15, anchor='w')

        self.version_label = AppStyles.create_label(
            self.sidebar,
            text=f"{self.version}",
            text_color=AppStyles.COLORS['text_disabled'],
            font=AppStyles.FONTS['small']
        )
        self.version_label.pack(pady=(10, 20), padx=15, anchor='w')

    def _create_panels(self):
        self.panels['download'] = DownloadPanel(
            self.content_frame,
            self._on_download
        )
        self.panels['search'] = SearchPanel(
            self.content_frame,
            self._on_search,
            self._on_download
        )
        self.panels['batch'] = BatchPanel(
            self.content_frame,
            self._on_download
        )
        self.panels['favorites'] = FavoritesPanel(
            self.content_frame,
            self.config,
            self._on_download
        )
        self.panels['history'] = HistoryPanel(
            self.content_frame,
            self._on_re_download
        )
        self.panels['settings'] = SettingsPanel(
            self.content_frame,
            self.config,
            self._on_settings_changed
        )

    def _show_panel(self, panel_id: str):
        self._current_panel = panel_id
        
        for pid, panel in self.panels.items():
            if pid == panel_id:
                panel.grid(row=0, column=0, sticky='nsew')
                if pid == 'history' and not hasattr(panel, '_loaded'):
                    panel._load_history()
                    panel._loaded = True
            else:
                panel.grid_forget()

        for pid, btn in self.nav_buttons:
            if pid == panel_id:
                btn.configure(fg_color=AppStyles.COLORS['accent_light'])
                btn.configure(text_color=AppStyles.COLORS['accent'])
            else:
                btn.configure(fg_color='transparent')
                btn.configure(text_color=AppStyles.COLORS['text_secondary'])

    def _toggle_theme(self):
        if self.current_theme == 'dark':
            self.current_theme = 'light'
            ctk.set_appearance_mode('light')
        else:
            self.current_theme = 'dark'
            ctk.set_appearance_mode('dark')

        AppStyles.set_theme(self.current_theme)
        self.config.set('theme', self.current_theme)
        self._refresh_styles()

    def _on_download(self, url_or_bvid: str, download_type: str, progress_callback: Optional[Callable] = None):
        download_panel = self.panels['download']
        
        def progress_wrapper(task_id, progress, status):
            if progress_callback:
                progress_callback(task_id, progress, status)
            download_panel.add_download_task(task_id, url_or_bvid, progress, status)

        def download_task():
            task_id = f"task_{int(time.time() * 1000)}_{hash(url_or_bvid)}"
            
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.downloader.download_video(url_or_bvid, download_type, lambda p, s: progress_wrapper(task_id, p, s))
                )
                loop.close()

                if result:
                    progress_wrapper(task_id, 100, "下载完成")
                    self.panels['history'].add_download(url_or_bvid, download_type, 'success')
                else:
                    progress_wrapper(task_id, 0, "下载失败")
                    self.panels['history'].add_download(url_or_bvid, download_type, 'failed')

            except Exception as e:
                progress_wrapper(task_id, 0, f"错误: {str(e)}")
                self.panels['history'].add_download(url_or_bvid, download_type, 'failed')

        thread = threading.Thread(target=download_task, daemon=True)
        thread.start()

    def _on_search(self, keyword: str, page: int = 1):
        try:
            results = self.api.search_videos(keyword, page)
            if not results:
                results = self.api.search_videos_v2(keyword, page)
            return results
        except Exception as e:
            return []

    def _on_batch_download(self, bvids: List[str], download_type: str, status_callback: Optional[Callable]):
        def batch_task():
            for bvid in bvids:
                def download_one(bvid=bvid):
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(
                            self.downloader.download_video(bvid, download_type)
                        )
                        loop.close()

                        if status_callback:
                            if result:
                                status_callback(bvid, "完成", True)
                                self.panels['history'].add_download(bvid, download_type, 'success')
                            else:
                                status_callback(bvid, "失败", False)
                                self.panels['history'].add_download(bvid, download_type, 'failed')
                    except Exception as e:
                        if status_callback:
                            status_callback(bvid, f"失败: {str(e)}", False)
                        self.panels['history'].add_download(bvid, download_type, 'failed')

                thread = threading.Thread(target=download_one, daemon=True)
                thread.start()

        thread = threading.Thread(target=batch_task, daemon=True)
        thread.start()

    def _on_favorites_download(self, bvids: List[str], download_type: str, status_callback: Optional[Callable]):
        self._on_batch_download(bvids, download_type, status_callback)

    def _on_re_download(self, bvid: str, download_type: str):
        self._on_download(bvid, download_type, None)
        self._show_panel('download')

    def _on_settings_changed(self, config):
        self.config = config

    def _setup_shortcuts(self):
        self.bind('<Control-q>', lambda e: self._on_closing())
        self.bind('<Control-Q>', lambda e: self._on_closing())

    def _refresh_styles(self):
        self.sidebar.configure(fg_color=AppStyles.COLORS['bg_medium'])
        
        if hasattr(self, 'logo_label'):
            self.logo_label.configure(text_color=AppStyles.COLORS['text_primary'])
        
        if hasattr(self, 'theme_switch'):
            self.theme_switch.configure(text_color=AppStyles.COLORS['text_secondary'])
        
        if hasattr(self, 'version_label'):
            self.version_label.configure(text_color=AppStyles.COLORS['text_disabled'])
        
        for pid, btn in self.nav_buttons:
            btn.configure(hover_color=AppStyles.COLORS['accent_light'])
            if pid == self._current_panel:
                btn.configure(fg_color=AppStyles.COLORS['accent_light'])
                btn.configure(text_color=AppStyles.COLORS['accent'])
            else:
                btn.configure(fg_color='transparent')
                btn.configure(text_color=AppStyles.COLORS['text_secondary'])

        self.content_frame.configure(fg_color=AppStyles.COLORS['bg_dark'])
        
        self._refresh_panel_styles()

    def _refresh_panel_styles(self):
        for panel in self.panels.values():
            panel.configure(fg_color=AppStyles.COLORS['bg_dark'])
            self._refresh_widget_styles(panel)

    def _refresh_widget_styles(self, parent):
        for child in parent.winfo_children():
            if hasattr(child, 'configure'):
                try:
                    child.configure(fg_color=AppStyles.COLORS['bg_card'])
                except:
                    pass
                try:
                    child.configure(text_color=AppStyles.COLORS['text_primary'])
                except:
                    pass
                try:
                    child.configure(border_color=AppStyles.COLORS['border'])
                except:
                    pass
                try:
                    child.configure(button_color=AppStyles.COLORS['accent'])
                except:
                    pass
            self._refresh_widget_styles(child)

    def _on_closing(self):
        from tkinter import messagebox
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            self.destroy()

    def run(self):
        self.mainloop()
