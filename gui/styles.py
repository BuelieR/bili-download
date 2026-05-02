import customtkinter as ctk
from typing import Dict, Tuple, Optional


class AppStyles:
    COLORS_LIGHT: Dict[str, str] = {
        'bg_dark': '#F5F5F5',
        'bg_medium': '#E8E8E8',
        'bg_light': '#FFFFFF',
        'bg_card': '#FFFFFF',
        'accent': '#0078D7',
        'accent_hover': '#005A9E',
        'accent_light': '#E6F4FA',
        'success': '#00B894',
        'warning': '#E57373',
        'error': '#EF5350',
        'info': '#42A5F5',
        'text_primary': '#1A1A1A',
        'text_secondary': '#6D6D6D',
        'text_disabled': '#B0B0B0',
        'border': '#E0E0E0',
        'border_light': '#F0F0F0'
    }

    COLORS_DARK: Dict[str, str] = {
        'bg_dark': '#1C1C1C',
        'bg_medium': '#252525',
        'bg_light': '#2D2D2D',
        'bg_card': '#252525',
        'accent': '#00D4AA',
        'accent_hover': '#00B894',
        'accent_light': '#364646',
        'success': '#00D4AA',
        'warning': '#FFB347',
        'error': '#FF6B6B',
        'info': '#4ECDC4',
        'text_primary': '#FFFFFF',
        'text_secondary': '#B8B8B8',
        'text_disabled': '#6B6B6B',
        'border': '#3A3A3A',
        'border_light': '#4A4A4A'
    }

    COLORS: Dict[str, str] = COLORS_DARK

    FONTS: Dict[str, tuple] = {
        'title': ('Segoe UI', 18, 'bold'),
        'heading': ('Segoe UI', 14, 'bold'),
        'normal': ('Segoe UI', 12),
        'small': ('Segoe UI', 10),
        'mono': ('Consolas', 11)
    }

    ROUNDS: Dict[str, int] = {
        'card': 8,
        'button': 4,
        'entry': 4,
        'progress': 2,
        'sidebar': 0
    }

    @classmethod
    def set_theme(cls, theme: str):
        if theme == 'light':
            cls.COLORS = cls.COLORS_LIGHT
        else:
            cls.COLORS = cls.COLORS_DARK

    @classmethod
    def get_color(cls, key: str) -> str:
        return cls.COLORS.get(key, '#1C1C1C')

    @classmethod
    def get_font(cls, key: str) -> tuple:
        return cls.FONTS.get(key, cls.FONTS['normal'])

    @classmethod
    def create_card_frame(cls, parent, **kwargs):
        frame = ctk.CTkFrame(
            parent,
            fg_color=cls.COLORS['bg_card'],
            corner_radius=cls.ROUNDS['card'],
            border_color=cls.COLORS['border'],
            border_width=1,
            **kwargs
        )
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
            corner_radius=cls.ROUNDS['button'],
            font=cls.FONTS['normal'],
            height=32,
            border_width=0,
            **kwargs
        )
        return button

    @classmethod
    def create_sidebar_button(cls, parent, text: str = "", **kwargs):
        button = ctk.CTkButton(
            parent,
            text=text,
            fg_color='transparent',
            hover_color=cls.COLORS['accent_light'],
            text_color=kwargs.pop('text_color', cls.COLORS['text_secondary']),
            corner_radius=cls.ROUNDS['sidebar'],
            font=cls.FONTS['normal'],
            height=40,
            border_width=0,
            anchor='w',
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
            corner_radius=cls.ROUNDS['entry'],
            font=cls.FONTS['normal'],
            height=32,
            border_width=1,
            placeholder_text_color=cls.COLORS['text_disabled'],
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
            corner_radius=cls.ROUNDS['entry'],
            font=kwargs.pop('font', cls.FONTS['normal']),
            border_width=1,
            **kwargs
        )
        return textbox

    @classmethod
    def create_progressbar(cls, parent, **kwargs):
        progressbar = ctk.CTkProgressBar(
            parent,
            progress_color=cls.COLORS['accent'],
            fg_color=cls.COLORS['bg_light'],
            corner_radius=cls.ROUNDS['progress'],
            border_width=0,
            height=6,
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

    @classmethod
    def create_checkbox(cls, parent, text: str = "", **kwargs):
        checkbox = ctk.CTkCheckBox(
            parent,
            text=text,
            fg_color=cls.COLORS['accent'],
            hover_color=cls.COLORS['accent_hover'],
            text_color=cls.COLORS['text_primary'],
            **kwargs
        )
        return checkbox
