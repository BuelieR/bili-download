"""
下载标签页
"""

import asyncio
import threading
import re
import customtkinter as ctk
from tkinter import filedialog, messagebox
from _Deprecated_gui._Deprecated_styles import COLORS, FONTS, SIZES


class DownloadTab:
    """下载标签页类"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.downloader = None
        self.api = None
        
        # 延迟初始化后端
        self.init_backend()
        
        # 创建UI
        self.create_ui()
    
    def init_backend(self):
        """初始化后端模块"""
        try:
            from config import Config
            from api.bili_api import BiliAPI
            from downloader.video_downloader import VideoDownloader
            
            self.config = Config()
            cookie = self.config.get('cookie')
            self.api = BiliAPI(cookie if cookie else None)
            self.downloader = VideoDownloader(self.config, self.api)
            
            # 使用安全的消息记录
            self._safe_log("后端初始化成功")
        except Exception as e:
            self._safe_log(f"初始化后端失败: {e}")

    def _safe_log(self, message: str):
        """安全地记录消息"""
        if hasattr(self.app, 'log_message') and hasattr(self.app, 'tasks_text'):
            self.app.log_message(message)
        else:
            print(message)
    
    def create_ui(self):
        """创建UI"""
        # 主框架
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=SIZES['padding'], pady=SIZES['padding'])
        
        # 输入区域
        self.create_input_section(main_frame)
        
        # 下载类型选择
        self.create_type_section(main_frame)
        
        # 收藏夹区域
        self.create_fav_section(main_frame)
        
        # 进度区域
        self.create_progress_section(main_frame)
    
    def create_input_section(self, parent):
        """创建输入区域"""
        input_frame = ctk.CTkFrame(parent)
        input_frame.pack(fill="x", pady=(0, SIZES['padding']))
        
        # BV号/链接输入
        label = ctk.CTkLabel(input_frame, text="BV号/链接:", font=FONTS["body"])
        label.grid(row=0, column=0, padx=(SIZES['small_padding'], 5), pady=SIZES['small_padding'], sticky="w")
        
        self.url_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="输入BV号或视频链接...",
            height=SIZES['entry_height'],
            width=500
        )
        self.url_entry.grid(row=0, column=1, padx=5, pady=SIZES['small_padding'], sticky="ew")
        
        download_btn = ctk.CTkButton(
            input_frame,
            text="下载",
            command=self.download_by_url,
            height=SIZES['button_height'],
            width=100,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"]
        )
        download_btn.grid(row=0, column=2, padx=5, pady=SIZES['small_padding'])
        
        # 搜索区域
        search_label = ctk.CTkLabel(input_frame, text="搜索:", font=FONTS["body"])
        search_label.grid(row=1, column=0, padx=(SIZES['small_padding'], 5), pady=SIZES['small_padding'], sticky="w")
        
        self.search_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="输入关键词搜索...",
            height=SIZES['entry_height'],
            width=400
        )
        self.search_entry.grid(row=1, column=1, padx=5, pady=SIZES['small_padding'], sticky="ew")
        
        search_btn = ctk.CTkButton(
            input_frame,
            text="搜索",
            command=self.search_videos,
            height=SIZES['button_height'],
            width=80
        )
        search_btn.grid(row=1, column=2, padx=5, pady=SIZES['small_padding'])
        
        # 配置网格权重
        input_frame.grid_columnconfigure(1, weight=1)
    
    def create_type_section(self, parent):
        """创建下载类型选择区域"""
        type_frame = ctk.CTkFrame(parent)
        type_frame.pack(fill="x", pady=(0, SIZES['padding']))
        
        label = ctk.CTkLabel(type_frame, text="下载类型:", font=FONTS["body"])
        label.pack(side="left", padx=SIZES['small_padding'])
        
        self.download_type = ctk.StringVar(value="audio")
        
        types = [
            ("🎬 仅视频", "video"),
            ("🎵 仅音频", "audio"),
            ("🎬+🎵 完整视频", "all")
        ]
        
        for text, value in types:
            radio = ctk.CTkRadioButton(
                type_frame,
                text=text,
                variable=self.download_type,
                value=value
            )
            radio.pack(side="left", padx=10)
    
    def create_fav_section(self, parent):
        """创建收藏夹区域"""
        fav_frame = ctk.CTkFrame(parent)
        fav_frame.pack(fill="x", pady=(0, SIZES['padding']))
        
        # 收藏夹ID输入
        id_frame = ctk.CTkFrame(fav_frame, fg_color="transparent")
        id_frame.pack(fill="x", pady=5)
        
        label = ctk.CTkLabel(id_frame, text="收藏夹ID:", font=FONTS["body"])
        label.pack(side="left", padx=SIZES['small_padding'])
        
        self.fav_entry = ctk.CTkEntry(
            id_frame,
            placeholder_text="输入收藏夹ID...",
            height=SIZES['entry_height'],
            width=200
        )
        self.fav_entry.pack(side="left", padx=5)
        
        public_btn = ctk.CTkButton(
            id_frame,
            text="下载公开收藏夹",
            command=self.download_public_fav,
            height=SIZES['button_height']
        )
        public_btn.pack(side="left", padx=5)
        
        private_btn = ctk.CTkButton(
            id_frame,
            text="下载私密收藏夹",
            command=self.download_private_fav,
            height=SIZES['button_height'],
            fg_color=COLORS["warning"]
        )
        private_btn.pack(side="left", padx=5)
        
        # 批量下载文件
        batch_frame = ctk.CTkFrame(fav_frame, fg_color="transparent")
        batch_frame.pack(fill="x", pady=5)
        
        batch_btn = ctk.CTkButton(
            batch_frame,
            text="📄 从文件批量下载",
            command=self.batch_from_file,
            height=SIZES['button_height'],
            fg_color=COLORS["success"]
        )
        batch_btn.pack(side="left", padx=SIZES['small_padding'])
    
    def create_progress_section(self, parent):
        """创建进度显示区域"""
        progress_frame = ctk.CTkFrame(parent)
        progress_frame.pack(fill="both", expand=True)
        
        # 当前下载信息
        self.current_label = ctk.CTkLabel(
            progress_frame,
            text="等待下载...",
            font=FONTS["body"]
        )
        self.current_label.pack(pady=(SIZES['small_padding'], 5))
        
        # 进度条
        self.download_progress = ctk.CTkProgressBar(progress_frame)
        self.download_progress.pack(fill="x", padx=SIZES['small_padding'], pady=5)
        self.download_progress.set(0)
        
        # 搜索结果显示区域
        self.search_result_text = ctk.CTkTextbox(progress_frame, height=200, font=FONTS["small"])
        self.search_result_text.pack(fill="both", expand=True, pady=(SIZES['small_padding'], 0))
    
    def _extract_bvid(self, url_or_bvid: str) -> str:
        """提取BV号"""
        # 如果已经是BV号
        if re.match(r'^BV[a-zA-Z0-9]{10}$', url_or_bvid):
            return url_or_bvid
        
        # 从URL提取
        patterns = [
            r'BV([a-zA-Z0-9]{10})',
            r'bilibili\.com/video/(BV[a-zA-Z0-9]+)',
            r'bilibili\.com/video/(av\\d+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url_or_bvid)
            if match:
                return match.group(1) if 'BV' in match.group(1) else match.group(0)
        return None
    
    def download_by_url(self):
        """通过URL下载"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("提示", "请输入BV号或链接")
            return
        
        def run():
            # 提取BV号
            bvid = self._extract_bvid(url)
            
            if not bvid:
                self.app.log_message(f"无效的BV号: {url}")
                return
            
            self.app.log_message(f"开始下载: {bvid}")
            download_type = self.download_type.get()
            
            # 运行异步下载
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.downloader.download_video(bvid, download_type)
                )
                if result:
                    self.app.log_message(f"✓ 下载完成: {result.name}")
                else:
                    self.app.log_message(f"✗ 下载失败: {bvid}")
            except Exception as e:
                self.app.log_message(f"下载错误: {e}")
            finally:
                loop.close()
        
        threading.Thread(target=run, daemon=True).start()
    
    def search_videos(self):
        """搜索视频"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return
        
        self.search_result_text.delete("1.0", "end")
        self.search_result_text.insert("1.0", "搜索中...\n")
        
        def run():
            try:
                results = self.api.search_videos(keyword, 1, 15)
                
                # 在主线程中更新UI
                self.app.after(0, lambda: self._update_search_results(results))
            except Exception as e:
                self.app.after(0, lambda: self.search_result_text.delete("1.0", "end"))
                self.app.after(0, lambda: self.search_result_text.insert("1.0", f"搜索失败: {e}"))
                self.app.log_message(f"搜索错误: {e}")
        
        threading.Thread(target=run, daemon=True).start()

    def _update_search_results(self, results):
        """更新搜索结果（在主线程中调用）"""
        self.search_result_text.delete("1.0", "end")
        if not results:
            self.search_result_text.insert("1.0", "未找到相关视频\n\n提示：\n1. 检查网络连接\n2. 尝试其他关键词\n3. 稍后重试")
            return
        
        for i, item in enumerate(results, 1):
            text = f"{i}. {item['title'][:50]}\n   作者: {item['author']} | BV号: {item['bvid']} | 播放: {item.get('play', 0)}\n\n"
            self.search_result_text.insert("end", text)
        
        self.app.log_message(f"搜索完成，找到 {len(results)} 个结果")
    
    def download_public_fav(self):
        """下载公开收藏夹"""
        fid = self.fav_entry.get().strip()
        if not fid:
            messagebox.showwarning("提示", "请输入收藏夹ID")
            return
        
        self._download_fav(fid, is_private=False)
    
    def download_private_fav(self):
        """下载私密收藏夹"""
        fid = self.fav_entry.get().strip()
        if not fid:
            messagebox.showwarning("提示", "请输入收藏夹ID")
            return
        
        # 检查Cookie
        cookie = self.config.get('cookie')
        if not cookie:
            messagebox.showwarning("提示", "下载私密收藏夹需要先设置SESSDATA\n请在设置标签页中配置")
            return
        
        self._download_fav(fid, is_private=True)
    
    def _download_fav(self, fid: str, is_private: bool):
        """下载收藏夹"""
        def run():
            self.app.log_message(f"正在获取收藏夹 {fid} 的内容...")
            try:
                items = self.api.get_favorites(int(fid), is_private)
            except Exception as e:
                self.app.log_message(f"获取收藏夹失败: {e}")
                return
            
            if not items:
                self.app.log_message("未获取到内容，请检查ID或登录状态")
                return
            
            total = len(items)
            self.app.log_message(f"找到 {total} 个视频")
            
            download_type = self.download_type.get()
            success = 0
            
            for i, item in enumerate(items, 1):
                bvid = item.get('bvid')
                title = item.get('title', bvid)
                self.app.log_message(f"[{i}/{total}] 下载: {title[:50]}")
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        self.downloader.download_video(bvid, download_type)
                    )
                    if result:
                        success += 1
                        self.app.log_message(f"  ✓ 成功")
                    else:
                        self.app.log_message(f"  ✗ 失败")
                except Exception as e:
                    self.app.log_message(f"  ✗ 错误: {e}")
                finally:
                    loop.close()
                
                # 更新进度
                self.app.update_status(f"下载中... {i}/{total}", i/total)
            
            self.app.log_message(f"收藏夹下载完成！成功: {success}/{total}")
            self.app.update_status("就绪", 0)
        
        threading.Thread(target=run, daemon=True).start()
    
    def batch_from_file(self):
        """从文件批量下载"""
        file_path = filedialog.askopenfilename(
            title="选择包含BV号的txt文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        def run():
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            bvids = []
            for line in lines:
                line = line.strip()
                if line:
                    bvid = self._extract_bvid(line)
                    if bvid:
                        bvids.append(bvid)
            
            if not bvids:
                self.app.log_message("未找到有效的BV号")
                return
            
            self.app.log_message(f"找到 {len(bvids)} 个视频")
            download_type = self.download_type.get()
            
            for i, bvid in enumerate(bvids, 1):
                self.app.log_message(f"[{i}/{len(bvids)}] 下载: {bvid}")
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(
                        self.downloader.download_video(bvid, download_type)
                    )
                    if result:
                        self.app.log_message(f"  ✓ 成功")
                    else:
                        self.app.log_message(f"  ✗ 失败")
                except Exception as e:
                    self.app.log_message(f"  ✗ 错误: {e}")
                finally:
                    loop.close()
                
                self.app.update_status(f"下载中... {i}/{len(bvids)}", i/len(bvids))
            
            self.app.log_message("批量下载完成！")
            self.app.update_status("就绪", 0)
        
        threading.Thread(target=run, daemon=True).start()