import customtkinter as ctk
from typing import Dict

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AppStyles:
    COLORS: Dict[str, str] = {
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

    FONTS: Dict[str, tuple] = {
        'title': ('Microsoft YaHei', 16, 'bold'),
        'heading': ('Microsoft YaHei', 13, 'bold'),
        'normal': ('Microsoft YaHei', 11),
        'small': ('Microsoft YaHei', 10),
        'mono': ('Consolas', 11)
    }

    @classmethod
    def get_color(cls, key: str) -> str:
        return cls.COLORS.get(key, cls.COLORS['bg_dark'])

    @classmethod
    def get_font(cls, key: str) -> tuple:
        return cls.FONTS.get(key, cls.FONTS['normal'])

    @classmethod
    def configure_appearance(cls):
        ctk.set_appearance_mode("dark")

    @classmethod
    def create_card_frame(cls, parent, **kwargs):
        frame = ctk.CTkFrame(parent, fg_color=cls.COLORS['bg_medium'], **kwargs)
        return frame

    @classmethod
    def create_label(cls, parent, text: str = "", **kwargs):
        label = ctk.CTkLabel(
            parent,
            text=text,
            text_color=kwargs.pop('text_color', cls.COLORS['text_primary']),
            **kwargs
        )
        return label

    @classmethod
    def create_button(cls, parent, text: str = "", **kwargs):
        button = ctk.CTkButton(
            parent,
            text=text,
            fg_color=kwargs.pop('fg_color', cls.COLORS['accent']),
            hover_color=kwargs.pop('hover_color', cls.COLORS['accent_hover']),
            text_color=kwargs.pop('text_color', 'white'),
            **kwargs
        )
        return button

    @classmethod
    def create_entry(cls, parent, **kwargs):
        entry = ctk.CTkEntry(
            parent,
            fg_color=cls.COLORS['bg_light'],
            text_color=cls.COLORS['text_primary'],
            border_color=cls.COLORS['border'],
            **kwargs
        )
        return entry

    @classmethod
    def create_textbox(cls, parent, **kwargs):
        textbox = ctk.CTkTextbox(
            parent,
            fg_color=cls.COLORS['bg_light'],
            text_color=cls.COLORS['text_primary'],
            border_color=cls.COLORS['border'],
            **kwargs
        )
        return textbox

    @classmethod
    def create_progressbar(cls, parent, **kwargs):
        progressbar = ctk.CTkProgressBar(
            parent,
            progress_color=cls.COLORS['accent'],
            fg_color=cls.COLORS['bg_light'],
            **kwargs
        )
        return progressbar

    @classmethod
    def create_switch(cls, parent, **kwargs):
        switch = ctk.CTkSwitch(
            parent,
            on_color=cls.COLORS['accent'],
            off_color=cls.COLORS['bg_light'],
            **kwargs
        )
        return switch

    @classmethod
    def create_optionmenu(cls, parent, **kwargs):
        optionmenu = ctk.CTkOptionMenu(
            parent,
            fg_color=cls.COLORS['bg_light'],
            button_color=cls.COLORS['accent'],
            text_color=cls.COLORS['text_primary'],
            **kwargs
        )
        return optionmenu

    @classmethod
    def create_segmented_button(cls, parent, **kwargs):
        segmented = ctk.CTkSegmentedButton(
            parent,
            fg_color=cls.COLORS['bg_light'],
            selected_color=cls.COLORS['accent'],
            text_color=cls.COLORS['text_primary'],
            **kwargs
        )
        return segmented
