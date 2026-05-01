import customtkinter as ctk
from typing import Callable, Dict, Any
from pathlib import Path

from gui.styles import AppStyles


class SettingsPanel(ctk.CTkFrame):
    def __init__(self, parent, config, on_settings_changed_callback: Callable = None):
        super().__init__(parent, fg_color=AppStyles.COLORS['bg_dark'])
        self.config = config
        self.on_settings_changed_callback = on_settings_changed_callback
        self.widgets = {}
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        title = AppStyles.create_label(self, text="⚙️ 设置", font=AppStyles.FONTS['title'])
        title.pack(pady=(20, 10), padx=20, anchor='w')

        scroll_frame = ctk.CTkScrollableFrame(self, fg_color='transparent')
        scroll_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self._create_path_section(scroll_frame)
        self._create_download_section(scroll_frame)
        self._create_cookie_section(scroll_frame)
        self._create_action_buttons(scroll_frame)

    def _create_section(self, parent, title: str):
        section = AppStyles.create_card_frame(parent)
        section.pack(fill='x', pady=10)

        section_title = AppStyles.create_label(
            section,
            text=title,
            font=AppStyles.FONTS['heading']
        )
        section_title.pack(pady=(15, 10), padx=15, anchor='w')

        return section

    def _create_path_section(self, parent):
        section = self._create_section(parent, "📁 保存路径")

        path_frame = ctk.CTkFrame(section, fg_color='transparent')
        path_frame.pack(fill='x', padx=15, pady=(0, 15))

        self.widgets['save_dir'] = AppStyles.create_entry(
            path_frame,
            placeholder_text="下载保存路径"
        )
        self.widgets['save_dir'].pack(side='left', fill='x', expand=True)

        browse_btn = AppStyles.create_button(
            path_frame,
            text="浏览",
            width=60,
            command=self._browse_save_dir
        )
        browse_btn.pack(side='left', padx=(10, 0))

    def _create_download_section(self, parent):
        section = self._create_section(parent, "⬇️ 下载设置")

        row1 = ctk.CTkFrame(section, fg_color='transparent')
        row1.pack(fill='x', padx=15, pady=(0, 10))

        lbl1 = AppStyles.create_label(row1, text="并行下载数:")
        lbl1.pack(side='left', padx=(0, 10))

        self.widgets['max_parallel'] = ctk.CTkOptionMenu(
            row1,
            values=["1", "2", "3", "5", "10"],
            fg_color=AppStyles.COLORS['bg_light'],
            button_color=AppStyles.COLORS['accent'],
            text_color=AppStyles.COLORS['text_primary'],
            dropdown_fg_color=AppStyles.COLORS['bg_medium']
        )
        self.widgets['max_parallel'].pack(side='left')

        row2 = ctk.CTkFrame(section, fg_color='transparent')
        row2.pack(fill='x', padx=15, pady=(0, 10))

        lbl2 = AppStyles.create_label(row2, text="限速 (MB/s):")
        lbl2.pack(side='left', padx=(0, 10))

        self.widgets['max_speed_mbps'] = AppStyles.create_entry(
            row2,
            width=100,
            placeholder_text="0"
        )
        self.widgets['max_speed_mbps'].pack(side='left')

        lbl3 = ctk.CTkLabel(row2, text="0表示不限速", text_color=AppStyles.COLORS['text_secondary'])
        lbl3.pack(side='left', padx=(10, 0))

        row3 = ctk.CTkFrame(section, fg_color='transparent')
        row3.pack(fill='x', padx=15, pady=(0, 15))

        lbl4 = AppStyles.create_label(row3, text="默认下载类型:")
        lbl4.pack(side='left', padx=(0, 10))

        self.widgets['download_type'] = ctk.CTkOptionMenu(
            row3,
            values=["audio", "video", "all"],
            fg_color=AppStyles.COLORS['bg_light'],
            button_color=AppStyles.COLORS['accent'],
            text_color=AppStyles.COLORS['text_primary'],
            dropdown_fg_color=AppStyles.COLORS['bg_medium']
        )
        self.widgets['download_type'].pack(side='left')

    def _create_cookie_section(self, parent):
        section = self._create_section(parent, "🔐 登录设置 (SESSDATA)")

        cookie_frame = ctk.CTkFrame(section, fg_color='transparent')
        cookie_frame.pack(fill='x', padx=15, pady=(0, 15))

        self.widgets['cookie'] = AppStyles.create_entry(
            cookie_frame,
            placeholder_text="输入SESSDATA (留空清除)"
        )
        self.widgets['cookie'].pack(fill='x', expand=True)

        hint = ctk.CTkLabel(
            section,
            text="获取方法: B站按F12 -> 存储 -> Cookie -> 找到SESSDATA",
            text_color=AppStyles.COLORS['text_secondary'],
            font=AppStyles.FONTS['small']
        )
        hint.pack(pady=(0, 15), padx=15, anchor='w')

    def _create_action_buttons(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color='transparent')
        btn_frame.pack(fill='x', pady=(10, 20))

        save_btn = AppStyles.create_button(
            btn_frame,
            text="保存设置",
            fg_color=AppStyles.COLORS['success'],
            hover_color='#45a049',
            command=self._save_settings
        )
        save_btn.pack(side='left', padx=(0, 10))

        reset_btn = AppStyles.create_button(
            btn_frame,
            text="重置默认",
            fg_color=AppStyles.COLORS['warning'],
            hover_color='#e68a00',
            command=self._reset_settings
        )
        reset_btn.pack(side='left')

        import_btn = AppStyles.create_button(
            btn_frame,
            text="导入",
            fg_color=AppStyles.COLORS['bg_light'],
            hover_color=AppStyles.COLORS['accent'],
            command=self._import_settings
        )
        import_btn.pack(side='right')

        export_btn = AppStyles.create_button(
            btn_frame,
            text="导出",
            fg_color=AppStyles.COLORS['bg_light'],
            hover_color=AppStyles.COLORS['accent'],
            command=self._export_settings
        )
        export_btn.pack(side='right', padx=(10, 0))

    def _load_settings(self):
        if not self.config:
            return

        self.widgets['save_dir'].delete(0, 'end')
        self.widgets['save_dir'].insert(0, self.config.get('save_dir', ''))

        self.widgets['max_parallel'].set(str(self.config.get('max_parallel', 3)))
        self.widgets['max_speed_mbps'].delete(0, 'end')
        self.widgets['max_speed_mbps'].insert(0, str(self.config.get('max_speed_mbps', 0)))
        self.widgets['download_type'].set(self.config.get('download_type', 'audio'))

        self.widgets['cookie'].delete(0, 'end')
        cookie_val = self.config.get('cookie', '')
        if cookie_val:
            self.widgets['cookie'].insert(0, cookie_val[:20] + "...")

    def _browse_save_dir(self):
        from tkinter import filedialog
        directory = filedialog.askdirectory(title="选择保存目录")
        if directory:
            self.widgets['save_dir'].delete(0, 'end')
            self.widgets['save_dir'].insert(0, directory)

    def _save_settings(self):
        if not self.config:
            return

        self.config.set('save_dir', self.widgets['save_dir'].get())
        self.config.set('max_parallel', int(self.widgets['max_parallel'].get()))
        self.config.set('max_speed_mbps', float(self.widgets['max_speed_mbps'].get()))
        self.config.set('download_type', self.widgets['download_type'].get())

        cookie = self.widgets['cookie'].get()
        if cookie and not cookie.endswith('...'):
            self.config.set('cookie', cookie)

        if self.on_settings_changed_callback:
            self.on_settings_changed_callback(self.config)

        from tkinter import messagebox
        messagebox.showinfo("成功", "设置已保存！")

    def _reset_settings(self):
        from tkinter import messagebox
        if messagebox.askyesno("确认", "确定要重置所有设置为默认值吗？"):
            if self.config.config_path.exists():
                self.config.config_path.unlink()
            self.config.load()
            self._load_settings()

    def _import_settings(self):
        from tkinter import filedialog, messagebox
        import json

        filename = filedialog.askopenfilename(
            title="导入设置",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                for key, value in settings.items():
                    self.config.set(key, value)
                self._load_settings()
                messagebox.showinfo("成功", "设置导入成功！")
            except Exception as e:
                messagebox.showerror("错误", f"导入失败: {str(e)}")

    def _export_settings(self):
        from tkinter import filedialog, messagebox
        import json

        filename = filedialog.asksaveasfilename(
            title="导出设置",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                settings = {
                    'save_dir': self.widgets['save_dir'].get(),
                    'max_parallel': int(self.widgets['max_parallel'].get()),
                    'max_speed_mbps': float(self.widgets['max_speed_mbps'].get()),
                    'download_type': self.widgets['download_type'].get()
                }
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", "设置导出成功！")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")

    def get_settings(self) -> Dict[str, Any]:
        return {
            'save_dir': self.widgets['save_dir'].get(),
            'max_parallel': int(self.widgets['max_parallel'].get()),
            'max_speed_mbps': float(self.widgets['max_speed_mbps'].get()),
            'download_type': self.widgets['download_type'].get(),
            'cookie': self.widgets['cookie'].get()
        }
