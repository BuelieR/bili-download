"""
视频下载核心模块
"""

import asyncio
import aiohttp
import aiofiles
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import time
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.speed_limit import SpeedLimiter
from utils.path_manager import PathManager


class VideoDownloader:
    """视频下载器类"""
    
    def __init__(self, config, api):
        self.config = config
        self.api = api
        self.speed_limiter = SpeedLimiter(config.get('max_speed_mbps', 0))
        self.path_manager = PathManager(config)
        self.max_retry = config.get('auto_retry', 3)
    
    async def download_video(self, bvid: str, download_type: str) -> Optional[Path]:
        """
        下载视频主流程
        """
        try:
            # 设置5分钟(60s*5=300s)超时
            return await asyncio.wait_for(
                self._download_video_impl(bvid, download_type),
                timeout=300
            )
        except asyncio.TimeoutError:
            print(f"下载超时 (超过5分钟)，跳过")
            return None
        except Exception as e:
            print(f"下载异常: {e}")
            return None

    async def _download_video_impl(self, bvid: str, download_type: str) -> Optional[Path]:
        """下载"""
        info = self.api.get_video_info(bvid)
        if not info:
            print(f"获取视频信息失败: {bvid}")
            return None
        
        print(f"标题: {info.title[:50]}... - {info.author}")
        
        if info.pages > 1:
            return await self._download_collection(bvid, info, download_type)
        else:
            return await self._download_single(bvid, info.cid, info.title, info.author, download_type)
    
    async def _download_single(self, bvid: str, cid: int, title: str, author: str, download_type: str) -> Optional[Path]:
        """下载单个视频"""
        play_data = self.api.get_download_url(bvid, cid)
        
        if not play_data or 'dash' not in play_data:
            print("无法获取下载链接")
            return None
        
        output_path = None
        
        if download_type == "audio":
            output_path = await self._download_audio_only(play_data, title, author)
        elif download_type == "video":
            output_path = await self._download_video_only(play_data, title, author)
        else:  # all
            output_path = await self._download_and_merge(play_data, title, author)
        
        return output_path
    
    async def _download_audio_only(self, play_data: Dict, title: str, author: str) -> Optional[Path]:
        """仅下载音频并转为MP3"""
        audio_url = play_data.get('dash', {}).get('audio', [{}])[0].get('base_url')
        if not audio_url:
            print("未找到音频流")
            return None
        
        temp_path = self.path_manager.get_temp_path(title)
        if await self._download_file(audio_url, temp_path):
            mp3_path = self.path_manager.get_output_path(title, author, 'mp3')
            if self._convert_to_mp3(temp_path, mp3_path):
                temp_path.unlink()
                return mp3_path
        return None
    
    async def _download_video_only(self, play_data: Dict, title: str, author: str) -> Optional[Path]:
        """仅下载视频(无声)"""
        video_url = play_data.get('dash', {}).get('video', [{}])[0].get('base_url')
        if not video_url:
            print("未找到视频流")
            return None
        
        video_path = self.path_manager.get_output_path(title, author, 'mp4')
        if await self._download_file(video_url, video_path):
            return video_path
        return None
    
    async def _download_and_merge(self, play_data: Dict, title: str, author: str) -> Optional[Path]:
        """下载视频和音频并合并"""
        video_list = play_data.get('dash', {}).get('video', [])
        audio_list = play_data.get('dash', {}).get('audio', [])
        
        if not video_list:
            print("未找到视频流")
            return None
        
        output_path = self.path_manager.get_output_path(title, author, 'mp4')
        if output_path.exists():
            print(f"文件已存在，跳过: {output_path.name}")
            return output_path
        
        if not audio_list:
            print("未找到独立音频流，尝试下载完整视频...")
            return await self._download_complete_video(play_data, title, author)
        
        video_url = video_list[0].get('base_url')
        audio_url = audio_list[0].get('base_url')
        
        if not video_url or not audio_url:
            print("无法获取下载链接")
            return None
        
        temp_video = self.path_manager.get_temp_path(f"{title}_video")
        temp_audio = self.path_manager.get_temp_path(f"{title}_audio")
        
        print("下载视频流...")
        video_ok = await self._download_file_with_progress(video_url, temp_video, "视频")
        
        #备用视频链接
        if not video_ok and len(video_list) > 1:
            print("尝试备用视频流...")
            video_url = video_list[1].get('base_url')
            if video_url:
                video_ok = await self._download_file_with_progress(video_url, temp_video, "视频备用")
        
        print("下载音频流...")
        audio_ok = await self._download_file_with_progress(audio_url, temp_audio, "音频")
        
        if video_ok and audio_ok:
            print(f"正在合并视频和音频...")
            if self._merge_video_audio(temp_video, temp_audio, output_path):
                temp_video.unlink()
                temp_audio.unlink()
                print(f"✓ 合并完成")
                return output_path
            else:
                print("合并失败")
        else:
            if not video_ok:
                print("视频流下载失败（可能是需要登录或链接已过期）")
            if audio_ok:
                audio_output = self.path_manager.get_output_path(title, author, 'mp3')
                temp_audio.rename(audio_output)
                print(f"已保存音频: {audio_output.name}")
        
        return None
    
    async def _download_complete_video(self, play_data: Dict, title: str, author: str) -> Optional[Path]:
        """下载完整视频（包含音频）"""
        # 尝试 durl 格式
        durl_list = play_data.get('durl', [])
        if durl_list:
            video_url = durl_list[0].get('url')
            if video_url:
                output_path = self.path_manager.get_output_path(title, author, 'mp4')
                if await self._download_file_with_progress(video_url, output_path, "完整视频"):
                    return output_path
        
        print("未找到可下载的完整视频")
        return None
    
    async def _download_file_with_progress(self, url: str, path: Path, name: str, retry: int = 0) -> bool:
        """下载"""
        if retry >= self.max_retry:
            return False
        
        try:
            timeout = aiohttp.ClientTimeout(total=120, connect=10)
            
            # 防盗链请求头
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.bilibili.com/",
                "Origin": "https://www.bilibili.com"
            }
            
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        print(f"  {name} HTTP {resp.status}")
                        return False
                    
                    content_length = resp.headers.get('content-length')
                    total_size = int(content_length) if content_length else 0
                    
                    path.parent.mkdir(parents=True, exist_ok=True)
                    
                    downloaded = 0
                    last_print = time.time()
                    last_percent = -1
                    
                    async with aiofiles.open(path, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(65536):  # 增大块大小到64KB
                            await self.speed_limiter.wait(len(chunk))
                            await f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 每0.5秒或每5%更新一次进度
                            current_time = time.time()
                            if total_size > 0:
                                percent = int(downloaded / total_size * 100)
                                if current_time - last_print > 0.5 or percent > last_percent:
                                    mb_downloaded = downloaded / 1024 / 1024
                                    mb_total = total_size / 1024 / 1024
                                    print(f"  {name}下载: {percent}% ({mb_downloaded:.1f}MB/{mb_total:.1f}MB)", end='\r')
                                    last_print = current_time
                                    last_percent = percent
                            else:
                                # 没有总大小时，每1秒更新一次
                                if current_time - last_print > 1:
                                    mb_downloaded = downloaded / 1024 / 1024
                                    print(f"  {name}下载: {mb_downloaded:.1f}MB", end='\r')
                                    last_print = current_time
                    
                    if total_size > 0:
                        mb_downloaded = downloaded / 1024 / 1024
                        mb_total = total_size / 1024 / 1024
                        print(f"  {name}下载完成: {mb_downloaded:.1f}MB/{mb_total:.1f}MB")
                    else:
                        mb_downloaded = downloaded / 1024 / 1024
                        print(f"  {name}下载完成: {mb_downloaded:.1f}MB")
                    return True
                    
        except asyncio.TimeoutError:
            print(f"\n  {name}下载超时，重试 {retry + 1}/{self.max_retry}")
            await asyncio.sleep(2)
            return await self._download_file_with_progress(url, path, name, retry + 1)
        except Exception as e:
            print(f"\n  {name}下载错误: {e}，重试 {retry + 1}/{self.max_retry}")
            await asyncio.sleep(2)
            return await self._download_file_with_progress(url, path, name, retry + 1)
    
    async def _download_file(self, url: str, path: Path, retry: int = 0) -> bool:
        if retry >= self.max_retry:
            return False
        
        try:
            timeout = aiohttp.ClientTimeout(total=60, connect=10)
            
            # 防盗链请求头
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.bilibili.com/",
                "Origin": "https://www.bilibili.com"
            }
            
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return False
                    
                    path.parent.mkdir(parents=True, exist_ok=True)
                    async with aiofiles.open(path, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(8192):
                            await self.speed_limiter.wait(len(chunk))
                            await f.write(chunk)
                    return True
        except Exception as e:
            print(f"下载失败: {e}")
            await asyncio.sleep(2)
            return await self._download_file(url, path, retry + 1)
        
    def _convert_to_mp3(self, input_path: Path, output_path: Path) -> bool:
        """使用FFmpeg转换音频为MP3"""
        cmd = [
            "ffmpeg", "-i", str(input_path),
            "-vn", "-acodec", "libmp3lame",
            "-q:a", "2", "-y", str(output_path)
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                print(f"FFmpeg错误: {result.stderr[:200]}")
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print("转换超时")
            return False
        except Exception as e:
            print(f"转换失败: {e}")
            return False
    
    def _merge_video_audio(self, video_path: Path, audio_path: Path, output_path: Path) -> bool:
        """合并视频和音频，带进度显示"""
        print("  正在合并 (可能需要1-2分钟)...")
        
        cmd = [
            "ffmpeg", "-i", str(video_path), "-i", str(audio_path),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest", "-y", str(output_path)
        ]
        
        try:
            # Popen 实时输出进度
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            # stderr 中的进度信息
            last_progress = 0
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                if 'time=' in line:
                    # 时间进度
                    import re
                    match = re.search(r'time=(\d{2}):(\d{2}):(\d{2})', line)
                    if match:
                        hours, minutes, seconds = map(int, match.groups())
                        total_seconds = hours * 3600 + minutes * 60 + seconds
                        # 估算进度
                        progress = min(int(total_seconds / 300 * 100), 99)
                        if progress > last_progress:
                            print(f"  合并进度: {progress}%", end='\r')
                            last_progress = progress
            
            process.wait(timeout=180)
            
            if process.returncode != 0:
                # 备用方案
                cmd2 = [
                    "ffmpeg", "-i", str(video_path), "-i", str(audio_path),
                    "-c:v", "libx264", "-c:a", "aac", "-crf", "23",
                    "-y", str(output_path)
                ]
                process2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=180)
                if process2.returncode != 0:
                    print(f"\n  FFmpeg错误: {process2.stderr[:200]}")
                    return False
            
            print("  合并进度: 100%")
            return True
            
        except subprocess.TimeoutExpired:
            process.kill()
            print("\n  合并超时")
            return False
        except Exception as e:
            print(f"\n  合并失败: {e}")
            return False
    
    async def _download_collection(self, bvid: str, info, download_type: str) -> Optional[Path]:
        """下载合集"""
        print(f"检测到合集，共 {info.pages} 个视频")
        collection_dir = self.path_manager.get_collection_dir(info.title)
        
        for page in range(1, info.pages + 1):
            print(f"\n下载第 {page}/{info.pages} 集...")
            page_info = self.api.get_page_info(bvid, page)
            if page_info:
                await self._download_single(
                    bvid, page_info['cid'],
                    f"{info.title}_P{page}", info.author,
                    download_type
                )
        
        return collection_dir