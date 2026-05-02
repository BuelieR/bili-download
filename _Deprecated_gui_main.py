#!/usr/bin/env python3
"""
B站下载器 - GUI版本
作者: 罗逸琳(Buelier)
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

import customtkinter as ctk
from _Deprecated_gui._Deprecated_main_window import MainWindow


def main():
    """GUI主函数"""
    # 设置外观模式
    ctk.set_appearance_mode("dark")  # 可选: "dark", "light", "system"
    ctk.set_default_color_theme("blue")  # 可选: "blue", "green", "dark-blue"
    
    # 创建主窗口
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()