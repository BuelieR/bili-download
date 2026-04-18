"""
GUI样式配置
"""

import customtkinter as ctk

# 颜色主题
COLORS = {
    "primary": "#00A1D6",      # B站粉色
    "primary_hover": "#00B5E5",
    "success": "#52C41A",
    "warning": "#FAAD14",
    "error": "#F5222D",
    "text": "#FFFFFF",
    "text_secondary": "#8A8A8A",
    "bg": "#1E1E1E",
    "bg_secondary": "#2D2D2D",
    "border": "#3A3A3A"
}

# 字体配置
FONTS = {
    "title": ("Microsoft YaHei", 20, "bold"),
    "heading": ("Microsoft YaHei", 16, "bold"),
    "body": ("Microsoft YaHei", 12),
    "small": ("Microsoft YaHei", 10),
    "code": ("Consolas", 11)
}

# 尺寸配置
SIZES = {
    "window_width": 900,
    "window_height": 700,
    "padding": 20,
    "small_padding": 10,
    "button_height": 35,
    "entry_height": 35
}

def configure_styles():
    """配置全局样式"""
    # 设置默认字体
    ctk.CTkFont(family="Microsoft YaHei", size=12)