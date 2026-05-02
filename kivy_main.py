#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import mainthread
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.core.text import LabelBase

LabelBase.register(name='Chinese', fn_regular='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')

from config import Config
from api.bili_api import BiliAPI
from downloader.video_downloader import VideoDownloader

Window.clearcolor = get_color_from_hex('#121212')


class DownloadScreen(Screen):
    def __init__(self, **kwargs):
        super(DownloadScreen, self).__init__(**kwargs)
        self.downloader = None
        self.api = None
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        nav_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        
        self.download_btn_nav = Button(
            text='📥 下载',
            size_hint_x=0.5,
            background_color=get_color_from_hex('#00D4AA'),
            color=get_color_from_hex('#FFFFFF'),
            font_size=14,
            bold=True,
            font_name='Chinese',
            disabled=True
        )
        nav_layout.add_widget(self.download_btn_nav)
        
        self.search_btn_nav = Button(
            text='🔍 搜索',
            size_hint_x=0.5,
            background_color=get_color_from_hex('#2A2A2A'),
            color=get_color_from_hex('#FFFFFF'),
            font_size=14,
            bold=True,
            font_name='Chinese'
        )
        self.search_btn_nav.bind(on_press=self.go_to_search)
        nav_layout.add_widget(self.search_btn_nav)
        layout.add_widget(nav_layout)
        
        title_label = Label(
            text='视频下载',
            font_size=20,
            color=get_color_from_hex('#FFFFFF'),
            bold=True,
            font_name='Chinese'
        )
        layout.add_widget(title_label)
        
        url_label = Label(
            text='BV号 / 视频链接:',
            font_size=14,
            color=get_color_from_hex('#B8B8B8'),
            font_name='Chinese'
        )
        layout.add_widget(url_label)
        
        self.url_input = TextInput(
            hint_text='输入BV号或完整链接',
            size_hint_y=None,
            height=40,
            background_color=get_color_from_hex('#2A2A2A'),
            foreground_color=get_color_from_hex('#FFFFFF'),
            hint_text_color=get_color_from_hex('#6B6B6B'),
            padding=[10, 10],
            font_name='Chinese'
        )
        layout.add_widget(self.url_input)
        
        type_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        type_label = Label(
            text='下载类型:',
            font_size=14,
            color=get_color_from_hex('#B8B8B8'),
            size_hint_x=0.3,
            font_name='Chinese'
        )
        type_layout.add_widget(type_label)
        
        self.download_type = Spinner(
            text='音频',
            values=['音频', '视频', '音视频'],
            size_hint_x=0.7,
            background_color=get_color_from_hex('#2A2A2A'),
            color=get_color_from_hex('#FFFFFF'),
            font_name='Chinese'
        )
        type_layout.add_widget(self.download_type)
        layout.add_widget(type_layout)
        
        self.download_btn = Button(
            text='开始下载',
            size_hint_y=None,
            height=45,
            background_color=get_color_from_hex('#00D4AA'),
            color=get_color_from_hex('#FFFFFF'),
            font_size=16,
            bold=True,
            font_name='Chinese'
        )
        self.download_btn.bind(on_press=self._start_download)
        layout.add_widget(self.download_btn)
        
        self.progress_bar = ProgressBar(
            size_hint_y=None,
            height=10,
            max=100
        )
        self.progress_bar.background_color = get_color_from_hex('#2A2A2A')
        self.progress_bar.color = get_color_from_hex('#00D4AA')
        self.progress_bar.value = 0
        layout.add_widget(self.progress_bar)
        
        self.status_label = Label(
            text='等待输入...',
            font_size=12,
            color=get_color_from_hex('#B8B8B8'),
            font_name='Chinese'
        )
        layout.add_widget(self.status_label)
        
        scroll_view = ScrollView(size_hint=(1, 1))
        self.task_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.task_list.bind(minimum_height=self.task_list.setter('height'))
        scroll_view.add_widget(self.task_list)
        layout.add_widget(scroll_view)
        
        self.add_widget(layout)
    
    def set_downloader(self, downloader, api):
        self.downloader = downloader
        self.api = api
    
    def go_to_search(self, instance):
        self.parent.current = 'search'
    
    @mainthread
    def _update_progress(self, progress, status):
        self.progress_bar.value = progress
        self.status_label.text = status
    
    def _start_download(self, instance):
        url_or_bvid = self.url_input.text.strip()
        if not url_or_bvid:
            self.status_label.text = '请输入BV号或链接'
            return
        
        type_map = {'音频': 'audio', '视频': 'video', '音视频': 'all'}
        download_type = type_map.get(self.download_type.text, 'audio')
        self.download_btn.disabled = True
        self.download_btn.text = '下载中...'
        
        import threading
        import asyncio
        
        def download_task():
            def progress_callback(progress, status):
                self._update_progress(progress, status)
            
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.downloader.download_video(url_or_bvid, download_type, progress_callback)
                )
                loop.close()
                
                if result:
                    self._update_progress(100, '下载完成')
                    self._add_task_item(url_or_bvid, '完成', True)
                else:
                    self._update_progress(0, '下载失败')
                    self._add_task_item(url_or_bvid, '失败', False)
            except Exception as e:
                self._update_progress(0, f'错误: {str(e)}')
                self._add_task_item(url_or_bvid, f'失败: {str(e)}', False)
            
            @mainthread
            def reset_button():
                self.download_btn.disabled = False
                self.download_btn.text = '开始下载'
            
            reset_button()
        
        thread = threading.Thread(target=download_task, daemon=True)
        thread.start()
    
    @mainthread
    def _add_task_item(self, bvid, status, success):
        task_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
            padding=[10, 5]
        )
        
        with task_layout.canvas.before:
            Color(*get_color_from_hex('#252525'))
            self.rect = RoundedRectangle(pos=task_layout.pos, size=task_layout.size, radius=[5])
            task_layout.bind(pos=self.update_rect, size=self.update_rect)
        
        bvid_label = Label(
            text=bvid[:30] + '...' if len(bvid) > 30 else bvid,
            font_size=12,
            color=get_color_from_hex('#FFFFFF'),
            size_hint_x=0.7,
            font_name='Chinese'
        )
        task_layout.add_widget(bvid_label)
        
        status_label = Label(
            text=status,
            font_size=12,
            color=get_color_from_hex('#00D4AA') if success else get_color_from_hex('#FF6B6B'),
            size_hint_x=0.3,
            font_name='Chinese'
        )
        task_layout.add_widget(status_label)
        
        self.task_list.add_widget(task_layout)
    
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class SearchScreen(Screen):
    def __init__(self, **kwargs):
        super(SearchScreen, self).__init__(**kwargs)
        self.api = None
        self.search_results = []
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        nav_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=45, spacing=10)
        
        self.download_btn_nav = Button(
            text='📥 下载',
            size_hint_x=0.5,
            background_color=get_color_from_hex('#2A2A2A'),
            color=get_color_from_hex('#FFFFFF'),
            font_size=14,
            bold=True,
            font_name='Chinese'
        )
        self.download_btn_nav.bind(on_press=self.go_to_download)
        nav_layout.add_widget(self.download_btn_nav)
        
        self.search_btn_nav = Button(
            text='🔍 搜索',
            size_hint_x=0.5,
            background_color=get_color_from_hex('#00D4AA'),
            color=get_color_from_hex('#FFFFFF'),
            font_size=14,
            bold=True,
            font_name='Chinese',
            disabled=True
        )
        nav_layout.add_widget(self.search_btn_nav)
        layout.add_widget(nav_layout)
        
        title_label = Label(
            text='搜索视频',
            font_size=20,
            color=get_color_from_hex('#FFFFFF'),
            bold=True,
            font_name='Chinese'
        )
        layout.add_widget(title_label)
        
        search_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=45)
        
        self.search_input = TextInput(
            hint_text='输入搜索关键词',
            size_hint_x=0.75,
            background_color=get_color_from_hex('#2A2A2A'),
            foreground_color=get_color_from_hex('#FFFFFF'),
            hint_text_color=get_color_from_hex('#6B6B6B'),
            padding=[10, 10],
            font_name='Chinese'
        )
        search_layout.add_widget(self.search_input)
        
        self.search_btn = Button(
            text='搜索',
            size_hint_x=0.25,
            background_color=get_color_from_hex('#00D4AA'),
            color=get_color_from_hex('#FFFFFF'),
            font_size=14,
            bold=True,
            font_name='Chinese'
        )
        self.search_btn.bind(on_press=self._do_search)
        search_layout.add_widget(self.search_btn)
        layout.add_widget(search_layout)
        
        scroll_view = ScrollView(size_hint=(1, 1))
        self.results_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.results_list.bind(minimum_height=self.results_list.setter('height'))
        scroll_view.add_widget(self.results_list)
        layout.add_widget(scroll_view)
        
        self.add_widget(layout)
    
    def set_api(self, api):
        self.api = api
    
    def go_to_download(self, instance):
        self.parent.current = 'download'
    
    def _do_search(self, instance):
        keyword = self.search_input.text.strip()
        if not keyword:
            return
        
        self.search_btn.disabled = True
        self.search_btn.text = '搜索中...'
        
        import threading
        
        def search_task():
            try:
                results = self.api.search_videos(keyword)
                self._display_results(results)
            except Exception as e:
                self._display_results([], str(e))
            
            @mainthread
            def reset_button():
                self.search_btn.disabled = False
                self.search_btn.text = '搜索'
            
            reset_button()
        
        thread = threading.Thread(target=search_task, daemon=True)
        thread.start()
    
    @mainthread
    def _display_results(self, results, error=None):
        self.results_list.clear_widgets()
        
        if error:
            error_label = Label(
                text=f'搜索失败: {error}',
                font_size=14,
                color=get_color_from_hex('#FF6B6B'),
                font_name='Chinese'
            )
            self.results_list.add_widget(error_label)
            return
        
        if not results:
            empty_label = Label(
                text='未找到结果',
                font_size=14,
                color=get_color_from_hex('#B8B8B8'),
                font_name='Chinese'
            )
            self.results_list.add_widget(empty_label)
            return
        
        self.search_results = results
        
        for i, item in enumerate(results):
            result_layout = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=100,
                padding=[10, 10]
            )
            
            with result_layout.canvas.before:
                Color(*get_color_from_hex('#252525'))
                self.rect = RoundedRectangle(pos=result_layout.pos, size=result_layout.size, radius=[8])
                result_layout.bind(pos=self.update_rect, size=self.update_rect)
            
            title_label = Label(
                text=item.get('title', '未知标题'),
                font_size=14,
                color=get_color_from_hex('#FFFFFF'),
                bold=True,
                font_name='Chinese',
                size_hint_y=None,
                height=40
            )
            result_layout.add_widget(title_label)
            
            meta_label = Label(
                text=f"👤 {item.get('author', '未知')} | 📺 {item.get('play', 0)}播放",
                font_size=12,
                color=get_color_from_hex('#B8B8B8'),
                font_name='Chinese'
            )
            result_layout.add_widget(meta_label)
            
            bvid_label = Label(
                text=f"BV号: {item.get('bvid', '')}",
                font_size=11,
                color=get_color_from_hex('#6B6B6B'),
                font_name='Chinese'
            )
            result_layout.add_widget(bvid_label)
            
            self.results_list.add_widget(result_layout)
    
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class BiliDownloaderApp(App):
    def build(self):
        self.config = Config()
        self.api = BiliAPI(self.config.get('cookie'))
        self.downloader = VideoDownloader(self.config, self.api)
        
        sm = ScreenManager()
        
        download_screen = DownloadScreen(name='download')
        download_screen.set_downloader(self.downloader, self.api)
        sm.add_widget(download_screen)
        
        search_screen = SearchScreen(name='search')
        search_screen.set_api(self.api)
        sm.add_widget(search_screen)
        
        return sm


if __name__ == '__main__':
    BiliDownloaderApp().run()