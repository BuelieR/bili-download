"""
配置管理模块
管理settings.json的读写
"""

import json
import os
import sys
import platform
from pathlib import Path
from typing import Any, Dict, Optional


if sys.platform.startswith('linux'):
    username = os.getlogin()
    save_dir = f"/home/{username}/BiliDownloads"
elif sys.platform.startswith('win'):
    save_dir = f"/BiliDownloads"
elif sys.platform.startswith('darwin'):
    username = os.getlogin()
    save_dir = f"/home/{username}/BiliDownloads"
else:
    save_dir = f"/BiliDownloads"

DEFAULT_CONFIG: Dict[str, Any] = {
    "save_dir": save_dir,
    "max_parallel": 3,
    "max_speed_mbps": 0,
    "filename_format": "${video_name}_AUTHOR_${video_author}",
    "download_type": "audio",
    "cookie": "",
    "quality": 80,
    "auto_retry": 3,
    "timeout": 30
}

"""
    `save_dir`: 默认下载地址
    `max_parallel`: 最大并行下载数量
    `max_speed_mbps`: 限速(0表示不限速,MB/s)
    `download_type`: 默认下载内容
    `cookie`: SESSDATA信息
    `quality`: 视频质量/80=高清, 64=流畅, 32=仅音频
    `auto_retry`: 下载失败重试次数
    `timeout`: 请求超时时间(秒)
}"""


class Config:
    """配置管理类"""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "settings.json"
        self.config_path = config_path
        self.config = self.load()
    
    def load(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content: 
                        print("配置文件为空，使用默认配置")
                        return DEFAULT_CONFIG.copy()
                    
                    user_config = json.loads(content)
                    return {**DEFAULT_CONFIG, **user_config}
            except json.JSONDecodeError as e:
                print(f"配置文件格式错误: {e}，使用默认配置")
                backup_path = self.config_path.with_suffix('.json.bak')
                self.config_path.rename(backup_path)
                print(f"已备份损坏的配置文件到: {backup_path}")
                return DEFAULT_CONFIG.copy()
            except IOError as e:
                print(f"配置文件读取失败: {e}，使用默认配置")
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()
    
    def save(self) -> None:
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"配置文件保存失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项"""
        self.config[key] = value
        self.save()
    
    def show_all(self) -> None:
        """显示所有配置"""
        print("\n当前配置:")
        print("-" * 40)
        for key, value in self.config.items():
            if key == "cookie":
                value = "***已设置***" if value else "(未设置)"
            print(f"  {key}: {value}")
        print("-" * 40)