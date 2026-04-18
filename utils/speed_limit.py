import time
import asyncio

class SpeedLimiter:
    def __init__(self, max_speed_mbps: float):
        self.max_speed = max_speed_mbps * 1024 * 1024 / 8  # MB/s -> bytes/s
        self.last_time = time.time()
        self.downloaded = 0
    
    async def wait(self, bytes_downloaded: int):
        if self.max_speed <= 0:
            return
        
        self.downloaded += bytes_downloaded
        now = time.time()
        elapsed = now - self.last_time
        
        expected_time = self.downloaded / self.max_speed
        if elapsed < expected_time:
            await asyncio.sleep(expected_time - elapsed)
        
        if elapsed >= 1.0:
            self.downloaded = 0
            self.last_time = now