#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
B站音频下载器 - GUI主程序
项目贡献者：罗逸琳(Buelier, LUO Yiling)，DeepSeek
"""

import sys
import tkinter as tk
from _Deprecated_gui._Deprecated_main_window import BiliDownloaderGUI
from api.bili_api import BiliAPI

# 尝试导入实际下载功能模块
try:
    # 这里导入你已经实现的功能代码
    # from bili_downloader import BiliDownloader
    HAS_BACKEND = False  # 如果没有后端，设为False
except ImportError:
    HAS_BACKEND = False
    print("警告：未找到下载功能模块，GUI将以演示模式运行")

class DummyDownloadController:
    """演示用的下载控制器（当实际功能代码未集成时使用）"""
    
    def __init__(self):
        self.settings = {}
    
    def download(self, url_or_bvid, download_format, progress_callback):
        """模拟下载"""
        import time
        print(f"模拟下载: {url_or_bvid}, 格式: {download_format}")
        
        for i in range(101):
            if progress_callback:
                progress_callback(i, f"下载中... {i}%")
            time.sleep(0.05)
        
        return True
    
    def search(self, keyword):
        """模拟搜索"""
        # 返回模拟数据
        return [
            {'title': f'{keyword} - 示例视频1', 'owner': {'name': 'UP主1'}, 'bvid': 'BV1xx411c7xx'},
            {'title': f'{keyword} - 示例视频2', 'owner': {'name': 'UP主2'}, 'bvid': 'BV1yy411d8yy'},
            {'title': f'{keyword} - 示例视频3', 'owner': {'name': 'UP主3'}, 'bvid': 'BV1zz411e9zz'},
        ] * 5  # 生成15个示例结果
    
    def update_settings(self, settings):
        """更新设置"""
        self.settings = settings
        print(f"设置已更新: {settings}")
    
    def stop_all(self):
        """停止所有下载"""
        print("停止所有下载任务")

def main():
    """主函数"""
    # 创建主窗口
    root = tk.Tk()
    
    # 创建GUI应用
    app = BiliDownloaderGUI(root)
    
    # 集成实际下载功能
    if HAS_BACKEND:
        # 使用实际的功能模块
        # from bili_downloader import BiliDownloader
        # controller = BiliDownloader()
        pass
    else:
        # 使用演示控制器
        controller = DummyDownloadController()
    
    app.set_download_controller(controller)
    
    # 设置窗口最小尺寸
    root.minsize(1000, 700)
    
    # 居中显示
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # 运行主循环
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)

if __name__ == "__main__":
    main()