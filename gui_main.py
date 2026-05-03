#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from api.bili_api import BiliAPI
from downloader.video_downloader import VideoDownloader
from gui.main_window import MainWindow

VERSION = "1.0.1"
def main():
    config = Config()

    cookie = config.get('cookie')
    api = BiliAPI(cookie)
    downloader = VideoDownloader(config, api)

    app = MainWindow(config, api, downloader)
    app.run()


if __name__ == "__main__":
    main()
