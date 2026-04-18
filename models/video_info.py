"""
视频信息数据模型
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class VideoInfo:
    """视频信息数据类"""
    bvid: str                    # BV号
    title: str                   # 视频标题
    author: str                  # 作者名称
    pubdate: int                 # 发布时间戳
    pages: int                   # 分页数量（合集）
    cid: int                     # 视频CID
    description: Optional[str] = None   # 视频描述
    cover_url: Optional[str] = None     # 封面URL
    duration: Optional[int] = None      # 视频时长(秒)
    aid: Optional[int] = None           # AV号
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.title:
            self.title = "未命名视频"
        
        if not self.author:
            self.author = "未知作者"
    
    def to_dict(self) -> dict:
        return {
            'bvid': self.bvid,
            'title': self.title,
            'author': self.author,
            'pubdate': self.pubdate,
            'pages': self.pages,
            'cid': self.cid,
            'description': self.description,
            'cover_url': self.cover_url,
            'duration': self.duration,
            'aid': self.aid
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VideoInfo':
        return cls(
            bvid=data.get('bvid', ''),
            title=data.get('title', ''),
            author=data.get('author', ''),
            pubdate=data.get('pubdate', 0),
            pages=data.get('pages', 1),
            cid=data.get('cid', 0),
            description=data.get('description'),
            cover_url=data.get('cover_url'),
            duration=data.get('duration'),
            aid=data.get('aid')
        )
    
    def __str__(self) -> str:
        return f"[{self.bvid}] {self.title} - {self.author}"


@dataclass
class VideoPage:
    """视频分页信息（用于合集）"""
    cid: int                     # 分页CID
    page: int                    # 页码
    title: str                   # 分页标题
    duration: Optional[int] = None  # 时长
    
    def __str__(self) -> str:
        return f"P{self.page}: {self.title}"


@dataclass
class DownloadTask:
    """下载任务信息"""
    bvid: str
    title: str
    author: str
    download_type: str  # video/mp3/audio
    output_path: str
    status: str = "pending"  # pending/downloading/completed/failed
    progress: float = 0.0
    error_msg: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'bvid': self.bvid,
            'title': self.title,
            'author': self.author,
            'download_type': self.download_type,
            'output_path': self.output_path,
            'status': self.status,
            'progress': self.progress,
            'error_msg': self.error_msg
        }