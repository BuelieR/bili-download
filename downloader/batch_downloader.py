"""
批量下载管理模块
"""

import asyncio
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))


class BatchDownloader:
    """批量下载管理器"""
    
    def __init__(self, downloader, max_concurrent: int = 3):
        self.downloader = downloader
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def download_batch(self, bvids: List[str], download_type: str):
        """批量下载多个视频"""
        tasks = []
        for bvid in bvids:
            tasks.append(self._download_with_limit(bvid, download_type))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success = sum(1 for r in results if r and not isinstance(r, Exception))
        print(f"\n批量下载完成: 成功 {success}/{len(bvids)}")
    
    async def _download_with_limit(self, bvid: str, download_type: str):
        """带并发限制的下载"""
        async with self.semaphore:
            return await self.downloader.download_video(bvid, download_type)