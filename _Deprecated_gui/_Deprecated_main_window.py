import tkinter as tk
from tkinter import ttk
import threading
from _Deprecated_gui._Deprecated_styles import AppStyles
from _Deprecated_gui._Deprecated_settings_panel import SettingsPanel
from _Deprecated_gui._Deprecated_download_panel import DownloadPanel
from _Deprecated_gui._Deprecated_search_panel import SearchPanel
from _Deprecated_gui._Deprecated_batch_panel import BatchPanel

class BiliDownloaderGUI:
    """B站下载器主GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("B站音频下载器 v1.0")
        self.root.geometry("1200x800")
        
        # 应用主题
        AppStyles.apply_theme(root)
        
        # 创建主框架 - 使用 pack
        main_container = ttk.Frame(root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建菜单
        self.create_menu()
        
        # 创建标签页
        self.create_notebook(main_container)
        
        # 下载控制回调
        self.download_controller = None
        
        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root, bg=AppStyles.COLORS['bg_medium'],
                         fg=AppStyles.COLORS['text_primary'])
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0, bg=AppStyles.COLORS['bg_medium'],
                           fg=AppStyles.COLORS['text_primary'])
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导入设置", command=self.import_settings)
        file_menu.add_command(label="导出设置", command=self.export_settings)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0, bg=AppStyles.COLORS['bg_medium'],
                           fg=AppStyles.COLORS['text_primary'])
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_notebook(self, parent):
        """创建标签页"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 下载页面
        self.download_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.download_frame, text="📥 下载器")
        self.download_panel = DownloadPanel(self.download_frame, self.on_download)
        
        # 搜索页面
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="🔍 搜索")
        self.search_panel = SearchPanel(self.search_frame, self.on_search, self.on_download)
        
        # 批量处理页面
        self.batch_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_frame, text="📋 批量处理")
        self.batch_panel = BatchPanel(self.batch_frame, self.on_batch_download)
        
        # 设置页面
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ 设置")
        self.settings_panel = SettingsPanel(self.settings_frame, self.on_settings_changed)
    
    def on_download(self, url_or_bvid, download_format, progress_callback):
        """下载回调"""
        if self.download_controller:
            import time
            task_id = f"task_{int(time.time() * 1000)}"
            
            # 添加到下载面板显示
            video_name = self.extract_video_name(url_or_bvid)
            self.download_panel.add_task_to_queue(task_id, video_name)
            
            # 在新线程中执行下载
            import threading
            def download_task():
                try:
                    result = self.download_controller.download(
                        url_or_bvid, 
                        download_format,
                        lambda progress, status: progress_callback(task_id, progress, status)
                    )
                    if result:
                        progress_callback(task_id, 100, "下载完成")
                except Exception as e:
                    progress_callback(task_id, 0, f"错误: {str(e)}")
            
            thread = threading.Thread(target=download_task, daemon=True)
            thread.start()
        else:
            print("下载控制器未设置")
    
    def on_search(self, keyword):
        """搜索回调"""
        if self.download_controller:
            try:
                results = self.download_controller.search(keyword)
                return results
            except Exception as e:
                print(f"搜索错误: {e}")
                return []
        return []
    
    def on_batch_download(self, url_list, download_format, status_callback):
        """批量下载回调"""
        if self.download_controller:
            import threading
            def batch_task():
                for url in url_list:
                    try:
                        status_callback(url, "下载中...", True)
                        self.download_controller.download(url, download_format, None)
                        status_callback(url, "下载完成", True)
                    except Exception as e:
                        status_callback(url, f"失败: {str(e)}", False)
            
            thread = threading.Thread(target=batch_task, daemon=True)
            thread.start()
    
    def on_settings_changed(self, settings):
        """设置变更回调"""
        if self.download_controller:
            self.download_controller.update_settings(settings)
    
    def extract_video_name(self, url_or_bvid):
        """提取视频名称"""
        return f"视频_{url_or_bvid[-8:]}"
    
    def set_download_controller(self, controller):
        """设置下载控制器"""
        self.download_controller = controller
    
    def import_settings(self):
        """导入设置"""
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
                messagebox.showinfo("成功", "设置导入成功！")
            except Exception as e:
                messagebox.showerror("错误", f"导入失败: {str(e)}")
    
    def export_settings(self):
        """导出设置"""
        from tkinter import filedialog, messagebox
        import json
        
        filename = filedialog.asksaveasfilename(
            title="导出设置",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                settings = self.settings_panel.get_settings()
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", "设置导出成功！")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def show_help(self):
        """显示帮助信息"""
        from tkinter import messagebox
        
        help_text = """B站音频下载器使用说明

1. 下载视频：
   - 在下载器页面输入BV号或视频链接
   - 选择下载格式后点击下载

2. 搜索视频：
   - 在搜索页面输入关键词
   - 双击搜索结果即可下载

3. 批量下载：
   - 在批量处理页面输入多个BV号
   - 每行一个，点击开始批量下载

4. 设置：
   - 可设置保存目录、并行下载数等
   - 支持自定义文件名格式

注意：请遵守B站相关使用条款。
"""
        messagebox.showinfo("使用说明", help_text)
    
    def show_about(self):
        """显示关于信息"""
        from tkinter import messagebox
        
        about_text = """B站音频下载器 v1.0

项目贡献者：
- 罗逸琳 (Buelier, LUO Yiling)
- DeepSeek

功能特性：
- 支持视频/音频下载
- 支持搜索功能
- 支持批量下载
- 支持收藏夹下载
- 跨平台支持

基于 Python3 + tkinter 开发
"""
        messagebox.showinfo("关于", about_text)
    
    def on_closing(self):
        """关闭窗口时的处理"""
        from tkinter import messagebox
        
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            if self.download_controller:
                self.download_controller.stop_all()
            self.root.destroy()