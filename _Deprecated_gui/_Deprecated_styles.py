import tkinter as tk
from tkinter import ttk
import colorsys

class AppStyles:
    """样式配置"""
    
    # 暗色
    COLORS = {
        'bg_dark': '#1E1E1E',
        'bg_medium': '#2D2D2D',
        'bg_light': '#3C3C3C',
        'accent': '#00A8FF',
        'accent_hover': '#0088CC',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'error': '#F44336',
        'text_primary': '#FFFFFF',
        'text_secondary': '#B0B0B0',
        'text_disabled': '#6B6B6B',
        'border': '#4A4A4A'
    }
    
    # 字体配置
    FONTS = {
        'title': ('Microsoft YaHei', 14, 'bold'),
        'heading': ('Microsoft YaHei', 12, 'bold'),
        'normal': ('Microsoft YaHei', 10),
        'small': ('Microsoft YaHei', 9),
        'mono': ('Consolas', 10)
    }
    
    @classmethod
    def apply_theme(cls, root):
        """应用主题到根窗口"""
        root.configure(bg=cls.COLORS['bg_dark'])
        
        # 配置ttk样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置各种组件样式
        style.configure('TFrame', background=cls.COLORS['bg_dark'])
        style.configure('TLabelframe', background=cls.COLORS['bg_dark'], 
                       foreground=cls.COLORS['text_primary'],
                       borderwidth=2, relief='solid')
        style.configure('TLabelframe.Label', background=cls.COLORS['bg_dark'],
                       foreground=cls.COLORS['text_primary'],
                       font=cls.FONTS['heading'])
        
        # 按钮样式
        style.configure('Accent.TButton', 
                       background=cls.COLORS['accent'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=cls.FONTS['normal'])
        style.map('Accent.TButton',
                 background=[('active', cls.COLORS['accent_hover']),
                           ('pressed', cls.COLORS['accent_hover'])])
        
        style.configure('Success.TButton',
                       background=cls.COLORS['success'],
                       foreground='white')
        style.map('Success.TButton',
                 background=[('active', '#45a049')])
        
        # 标签样式
        style.configure('TLabel', background=cls.COLORS['bg_dark'],
                       foreground=cls.COLORS['text_primary'],
                       font=cls.FONTS['normal'])
        style.configure('Heading.TLabel', font=cls.FONTS['heading'])
        style.configure('Title.TLabel', font=cls.FONTS['title'])
        
        # 输入框样式
        style.configure('TEntry', fieldbackground=cls.COLORS['bg_light'],
                       foreground=cls.COLORS['text_primary'],
                       borderwidth=0,
                       padding=5)
        style.configure('TCombobox', fieldbackground=cls.COLORS['bg_light'],
                       foreground=cls.COLORS['text_primary'])
        
        # 进度条样式
        style.configure('TProgressbar', background=cls.COLORS['accent'],
                       troughcolor=cls.COLORS['bg_light'],
                       borderwidth=0)
        
        # 滚动条样式
        style.configure('Vertical.TScrollbar', 
                       background=cls.COLORS['bg_light'],
                       troughcolor=cls.COLORS['bg_dark'],
                       borderwidth=0)
        
        return style

class CustomWidgets:
    """美化组件"""
    
    @staticmethod
    def create_card(parent, **kwargs):
        """卡片容器"""
        card = tk.Frame(parent, bg=AppStyles.COLORS['bg_medium'],
                       relief='flat', bd=0, **kwargs)
        return card
    
    @staticmethod
    def create_separator(parent, orientation='horizontal', **kwargs):
        """分隔线"""
        if orientation == 'horizontal':
            sep = tk.Frame(parent, height=2, bg=AppStyles.COLORS['border'], **kwargs)
        else:
            sep = tk.Frame(parent, width=2, bg=AppStyles.COLORS['border'], **kwargs)
        return sep