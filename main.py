#!/usr/bin/env python3
import asyncio
import sys
from config import Config
from api.bili_api import BiliAPI
from downloader.video_downloader import VideoDownloader
from cli import BiliCLI

def main():
    config = Config()
    
    # 登录(如需要)
    cookie = config.get('cookie')
    if not cookie:
        cookie = input("请输入SESSDATA(按回车跳过): ").strip()
        if cookie:
            config.set('cookie', cookie)
    
    api = BiliAPI(cookie)
    downloader = VideoDownloader(config, api)
    cli = BiliCLI(downloader, api, config)
    
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n已退出")
        sys.exit(0)

if __name__ == "__main__":
    main()