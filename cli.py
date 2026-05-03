"""
CLI交互界面模块
"""
VERSION = "1.0.1"

import time
import asyncio
import os
import sys
import platform
from pathlib import Path
from typing import Optional, List

try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, BarColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("提示: 安装rich库可获得更好的界面效果: pip install rich")
    class Console:
        def print(self, *args, **kwargs):
            print(*args)
    
    class Prompt:
        @staticmethod
        def ask(prompt, choices=None, default=None):
            if choices:
                prompt = f"{prompt} [{','.join(choices)}]"
            if default:
                prompt = f"{prompt} (默认: {default})"
            return input(f"{prompt}: ").strip() or default
    
    class Confirm:
        @staticmethod
        def ask(prompt):
            return input(f"{prompt} (y/n): ").strip().lower() == 'y'


class BiliCLI:
    """CLI交互界面类"""
    
    def __init__(self, downloader, api, config):
        self.downloader = downloader
        self.api = api
        self.config = config
        self.console = Console() if RICH_AVAILABLE else None
    
    def _print(self, text: str, color: str = ""):
        """打印文本"""
        print(text)
    
    def _print_menu(self):
        """打印菜单"""
        menu_text = """
╔══════════════════════════════════════╗
║        B站下载器 - 主菜单            ║
╠══════════════════════════════════════╣
║ 1. 搜索视频                          ║
║ 2. 通过BV号/链接下载                 ║
║ 3. 批量下载(从txt文件)               ║
║ 4. 下载公开收藏夹                    ║
║ 5. 下载私密收藏夹(需登录)            ║
║ 6. 设置                              ║
║ 7. 退出                              ║
╚══════════════════════════════════════╝
"""
        print(menu_text)
    
    def run(self):
        """主循环"""
        while True:
            self._print_menu()
            choice = Prompt.ask("请选择", choices=["1", "2", "3", "4", "5", "6", "7"])
            
            if choice == "1":
                asyncio.run(self.search_and_download())
            elif choice == "2":
                asyncio.run(self.download_by_url())
            elif choice == "3":
                asyncio.run(self.batch_from_file())
            elif choice == "4":
                asyncio.run(self.download_public_fav())
            elif choice == "5":
                asyncio.run(self.download_private_fav())
            elif choice == "6":
                self.settings_menu()
            elif choice == "7":
                print("\n再见！")
                break
    
    async def search_and_download(self):
        """搜索&下载"""
        keyword = Prompt.ask("\n请输入搜索关键词")
        page = 1
        
        while True:
            print(f"\n正在搜索第{page}页...")
            results = self.api.search_videos(keyword, page, 15)
            
            if not results:
                print("没有更多结果了")
                break
            
            # 显示结果
            print("\n" + "-" * 80)
            print(f"{'序号':<4} {'标题':<40} {'作者':<15} {'BV号':<12}")
            print("-" * 80)
            for i, item in enumerate(results, 1):
                title = item['title'][:38] + ".." if len(item['title']) > 40 else item['title']
                author = item['author'][:13] + ".." if len(item['author']) > 15 else item['author']
                print(f"{i:<4} {title:<40} {author:<15} {item['bvid']:<12}")
            print("-" * 80)
            
            choice = Prompt.ask(
                "\n输入序号下载(0下一页/-1上一页/q退出)",
                default="q"
            )
            
            if choice.lower() == 'q':
                break
            elif choice == "0":
                page += 1
            elif choice == "-1" and page > 1:
                page -= 1
            elif choice.isdigit() and 1 <= int(choice) <= len(results):
                selected = results[int(choice) - 1]
                await self._download_with_choice(selected['bvid'])
                break
    
    async def download_by_url(self):
        """通过URL或BV号下载"""
        url_or_bvid = Prompt.ask("\n请输入BV号或完整链接")
        
        bvid = self.api.get_bvid_from_url(url_or_bvid)
        if not bvid:
            print("无效的BV号或链接")
            return
        
        await self._download_with_choice(bvid)
    
    async def batch_from_file(self):
        """从txt文件批量下载"""
        file_path = Prompt.ask("\n请输入txt文件路径(每行一个BV号或链接)")
        
        path = Path(file_path)
        if not path.exists():
            print("文件不存在")
            return
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        bvids = []
        for line in lines:
            line = line.strip()
            if line:
                bvid = self.api.get_bvid_from_url(line)
                if bvid:
                    bvids.append(bvid)
        
        if not bvids:
            print("未找到有效的BV号")
            return
        
        print(f"找到 {len(bvids)} 个视频")
        download_type = self._get_download_type()
        
        for i, bvid in enumerate(bvids, 1):
            print(f"\n[{i}/{len(bvids)}] 下载: {bvid}")
            await self.downloader.download_video(bvid, download_type)
        
        print(f"\n批量下载完成！")
    
    async def download_public_fav(self):
        """下载公开收藏夹"""
        fid = Prompt.ask("\n请输入收藏夹ID(media_id)")
        
        if not fid.isdigit():
            print("请输入有效的数字ID")
            return
        
        await self._download_fav(int(fid), is_private=False)
    
    async def download_private_fav(self):
        """下载私密收藏夹"""
        # 检查登录状态
        cookie = self.config.get('cookie')
        if not cookie:
            print("需要登录才能下载私密收藏夹")
            if Confirm.ask("是否现在设置SESSDATA?"):
                cookie = Prompt.ask("请输入SESSDATA")
                if cookie:
                    self.config.set('cookie', cookie)
                    self.api.set_cookie(cookie)
                else:
                    print("未设置Cookie，无法下载私密内容")
                    return
            else:
                return
        
        fid = Prompt.ask("请输入收藏夹ID(media_id)")
        
        if not fid.isdigit():
            print("请输入有效的数字ID")
            return
        
        await self._download_fav(int(fid), is_private=True)
    
    async def _download_fav(self, fid: int, is_private: bool):
        """下载收藏夹内容"""
        print(f"正在获取收藏夹内容...")
        items = self.api.get_favorites(fid, is_private)
        
        if not items:
            print("未获取到内容，请检查ID是否正确或登录状态")
            return
        
        total = len(items)
        print(f"\n找到 {total} 个视频")
        download_type = self._get_download_type()
        
        success_count = 0
        fail_count = 0
        
        start_time = time.time()
        
        for i, item in enumerate(items, 1):
            bvid = item.get('bvid')
            title = item.get('title', bvid)
            
            # 显示进度条
            percent = (i - 1) / total * 100
            elapsed = time.time() - start_time
            if i > 1:
                eta = elapsed / (i - 1) * (total - i + 1)
                eta_min = int(eta // 60)
                eta_sec = int(eta % 60)
                print(f"\n[{i}/{total}] ({percent:.0f}%) 预计剩余: {eta_min}分{eta_sec}秒")
            else:
                print(f"\n[{i}/{total}]")
            
            print(f"下载: {title[:50]}...")
            
            result = await self.downloader.download_video(bvid, download_type)
            if result:
                success_count += 1
                print(f"✓ 成功: {result.name}")
            else:
                fail_count += 1
                print(f"✗ 失败")
        
        total_time = time.time() - start_time
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        
        print(f"\n{'='*50}")
        print(f"收藏夹下载完成！")
        print(f"成功: {success_count}, 失败: {fail_count}")
        print(f"总耗时: {minutes}分{seconds}秒")
        print(f"{'='*50}")
    
    async def _download_with_choice(self, bvid: str):
        """选择下载类型并下载"""
        download_type = self._get_download_type()
        
        print(f"\n准备下载: {bvid}")
        result = await self.downloader.download_video(bvid, download_type)
        
        if result:
            print(f"\n✓ 下载完成: {result}")
        else:
            print("\n✗ 下载失败")
    
    def _get_download_type(self) -> str:
        """获取下载类型"""
        print("\n下载类型说明:")
        print("  video - 仅视频(无声MP4)")
        print("  audio - 仅音乐(MP3)")
        print("  all   - 完整视频(含声音)")
        
        type_choice = Prompt.ask(
            "选择下载类型",
            choices=["video", "audio", "all"],
            default=self.config.get('download_type', 'audio')
        )
        return type_choice
    
    def settings_menu(self):
        """设置菜单"""
        while True:
            print("\n" + "=" * 50)
            print("设置菜单")
            print("=" * 50)
            self.config.show_all()
            print("\n1. 修改保存目录")
            print("2. 修改并行下载数量")
            print("3. 修改下载速度限制(MB/s)")
            print("4. 修改文件名格式")
            print("5. 修改默认下载类型")
            print("6. 设置Cookie(SESSDATA)")
            print("7. 重置所有设置")
            print("8. 返回主菜单")
            print(f"当前版本: {VERSION} | 当前系统: {sys.platform}",end="\n\n")
            
            choice = Prompt.ask("请选择", choices=["clear","1", "2", "3", "4", "5", "6", "7", "8"])
            
            if choice == "1":
                new_dir = Prompt.ask("请输入新的保存目录", default=self.config.get('save_dir'))
                self.config.set('save_dir', new_dir)
                print(f"保存目录已设置为: {new_dir}")
            
            elif choice == "2":
                new_parallel = Prompt.ask("请输入并行下载数量(1-10)", default="3")
                self.config.set('max_parallel', int(new_parallel))
                print(f"并行下载数量已设置为: {new_parallel}")
            
            elif choice == "3":
                new_speed = Prompt.ask("请输入速度限制MB/s(0表示不限速)", default="0")
                self.config.set('max_speed_mbps', float(new_speed))
                print(f"速度限制已设置为: {new_speed} MB/s")
            
            elif choice == "4":
                print("\n可用变量:")
                print("  ${video_name} - 视频名称")
                print("  ${video_author} - 视频作者")
                print("  ${video_time} - 发布时间")
                print("  ${download_time} - 下载时间")
                print("  ${ID} - 重名编号")
                new_format = Prompt.ask("请输入文件名格式", default=self.config.get('filename_format'))
                self.config.set('filename_format', new_format)
                print(f"文件名格式已设置为: {new_format}")
            
            elif choice == "5":
                new_type = Prompt.ask("默认下载类型", choices=["video", "mp3", "audio"])
                self.config.set('download_type', new_type)
                print(f"默认下载类型已设置为: {new_type}")
            
            elif choice == "6":
                new_cookie = Prompt.ask("请输入SESSDATA(留空清除)")
                self.config.set('cookie', new_cookie)
                if new_cookie:
                    self.api.set_cookie(new_cookie)
                    print("Cookie已设置")
                else:
                    print("Cookie已清除")
            
            elif choice == "7":
                if Confirm.ask("确认重置所有设置?"):
                    # 删除配置文件重新加载
                    if self.config.config_path.exists():
                        self.config.config_path.unlink()
                    self.config.load()
                    print("已重置所有设置")
            
            elif choice == "8":
                break

            elif choice == "clear":
                if sys.platform.startswith('linux'):
                    os.system("clear")
                elif sys.platform.startswith('win'):
                    os.system("cls")
                else:
                    print("不支持的系统")

            else:
                print("无效选择")
                continue