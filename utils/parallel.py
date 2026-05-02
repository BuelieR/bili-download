"""
并行下载控制模块
"""

import asyncio
from typing import List, Callable, Any, Optional


class ParallelDownloader:
    """并行下载控制器"""
    
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.tasks: List[asyncio.Task] = []
    
    async def run_with_limit(self, coro, *args, **kwargs):
        """并发限制的运行协程"""
        async with self.semaphore:
            return await coro(*args, **kwargs)
    
    def add_task(self, coro, *args, **kwargs):
        """下载任务"""
        task = asyncio.create_task(self.run_with_limit(coro, *args, **kwargs))
        self.tasks.append(task)
        return task
    
    async def wait_all(self):
        """等待任务完成"""
        if self.tasks:
            results = await asyncio.gather(*self.tasks, return_exceptions=True)
            self.tasks.clear()
            return results
        return []
    
    def cancel_all(self):
        """取消所有任务"""
        for task in self.tasks:
            if not task.done():
                task.cancel()
    
    @property
    def pending_count(self) -> int:
        """待处理任务数"""
        return sum(1 for t in self.tasks if not t.done())
    
    @property
    def completed_count(self) -> int:
        """已完成任务数"""
        return sum(1 for t in self.tasks if t.done())


class TaskQueue:
    """任务队列"""
    
    def __init__(self, max_size: int = 100):
        self.queue = asyncio.Queue(maxsize=max_size)
        self.results = []
    
    async def put(self, item):
        """添加任务"""
        await self.queue.put(item)
    
    async def get(self):
        """获取任务"""
        return await self.queue.get()
    
    def task_done(self):
        """标记任务完成"""
        self.queue.task_done()
    
    async def join(self):
        """等待任务完成"""
        await self.queue.join()
    
    def empty(self) -> bool:
        """队列是否为空"""
        return self.queue.empty()
    
    def size(self) -> int:
        """队列大小"""
        return self.queue.qsize()