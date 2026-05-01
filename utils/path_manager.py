"""
文件路径和文件名管理
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Dict


class PathManager:
    """路径管理器类"""
    
    def __init__(self, config):
        self.format_str = config.get('filename_format', '${video_name}_AUTHOR_${video_author}')
        self.save_dir = Path(config.get('save_dir'))
        self.temp_dir = self.save_dir / ".temp"
    
    def _sanitize_filename(self, name: str) -> str:
        """移除非法字符"""
        if not name:
            return "未命名"
        # 移除Windows/Linux文件名中的非法字符
        return re.sub(r'[<>:"/\\|?*]', '_', name).strip()
    
    def format_filename(self, video_info: Dict, index: int = 0) -> str:
        """
        根据模板格式化文件名
        :param video_info: 视频信息字典
        :param index: 重名文件编号(0表示不编号)
        :return: 格式化后的文件名(不含扩展名)
        """
        def replacer(match):
            key = match.group(1)
            if key == 'video_name':
                return self._sanitize_filename(video_info.get('title', '未命名'))
            elif key == 'video_time':
                ts = video_info.get('pubdate', 0)
                return datetime.fromtimestamp(ts).strftime('%Y%m%d') if ts else ''
            elif key == 'video_author':
                return self._sanitize_filename(video_info.get('author', '未知作者'))
            elif key == 'download_time':
                return datetime.now().strftime('%Y%m%d_%H%M%S')
            elif key == 'ID':
                return str(index) if index > 0 else ''
            return match.group(0)
        
        result = re.sub(r'\${(video_name|video_time|video_author|download_time|ID)}', replacer, self.format_str)
        
        # 处理空值和多余的下划线
        result = re.sub(r'_{2,}', '_', result)
        result = result.strip('_')
        
        return result if result else "download"
    
    def get_output_path(self, title: str, author: str, ext: str, index: int = 0) -> Path:
        """获取输出文件路径"""
        video_info = {'title': title, 'author': author}
        filename = self.format_filename(video_info, index)
        
        # 处理重名
        final_path = self.save_dir / f"{filename}.{ext}"
        counter = 1
        while final_path.exists():
            new_filename = self.format_filename(video_info, counter)
            final_path = self.save_dir / f"{new_filename}.{ext}"
            counter += 1
        
        return final_path
    
    def get_collection_dir(self, collection_name: str) -> Path:
        """获取合集文件夹路径"""
        dir_name = self._sanitize_filename(collection_name)
        collection_dir = self.save_dir / dir_name
        collection_dir.mkdir(parents=True, exist_ok=True)
        return collection_dir
    
    def get_temp_path(self, name: str) -> Path:
        """获取临时文件路径"""
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        safe_name = self._sanitize_filename(name)
        return self.temp_dir / f"{safe_name}.temp"