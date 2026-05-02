**中文 ( CHINESE ) |  [ English ( 英文 ) ](#)  |  [ More Languages (更多语言) ](#)**
# 简介
**该工具可以帮助你愉快地在`Windows`(电脑的Windows系统坏了所以没有打包，求好心人帮个忙打包下exe)/`Linux`/`Android`(Termux&ZeroTermux等软件)等平台上面下载B站上面下载视频。此工具主要为下载收藏夹(无论是`公开的`还是`私有的`，都可以下载)而生，~~毕竟这就是因为我实在找不到能满足我需求的工具而做的一堆BUG~~**

# 免责声明(避雷)
**由于本人审美和GUI/WEB编写技术烂的一批，GUI及WEB版本均大量使用AI(DeepSeek&DouBao&FittenCode)，如出BUG，将不会及时修复，请先尝试使用AI修复（？用魔法打败魔法么？emmm...）。如不行，请移步`CLI版本`。欢迎各位大佬完善本项目。**

# 下载&使用
| 平台 | Windows | Linux Debian系 | Android(Termux) |
| --- | --- | --- | --- |
| 下载 | [电脑Win系统坏了，QWQ](#) | [点击下载](https://github.com/BuelieR/bili-download/releases/download/R_v1.0.0/bili-downloader_1.0.0_all_linux.deb) | [点击下载](https://github.com/BuelieR/bili-download/releases/download/R_v1.0.0/bili-downloader_1.0.0_all_linux.deb) |
| 镜像 | [电脑Win系统坏了，QWQ](#) | [点击下载](#) | [点击下载](#) |
| 网页版 | [电脑Win系统坏了，QWQ](#) | [点击下载](https://github.com/BuelieR/bili-download/releases/download/R_v1.0.0/bili-downloader-web_1.0.0_all_linux.deb) | [点击下载](https://github.com/BuelieR/bili-download/releases/download/R_v1.0.0/bili-downloader-web_1.0.0_all_linux.deb) |

# 编译
* **请先安装`FFmpeg`&`pyinstaller`，这是本项目的依赖**
* **执行`pip install -r requirements.txt`以安装`CLI`版本依赖**
	* **`pip install -r requirements-gui.txt`安装`GUI`版本(现已废弃)**
	* **`pip install -r requirements-web.txt`安装`WEB`(基于Flask)版本(BUG++)**
* **执行`python3 <main.py/web_app.py/_Deprecated_gui_main.py文件路径>`以测试(推荐在虚拟环境运行)**
* **执行`package.sh`以打包`CLI`版程序(Linux Debian系)**
	* **执行`package_web.sh`以打包`WEB`(FLask)版程序(Linux Debian系)**
	* **打包GUI版本请自行修改`package.sh`中`MAIN_FILE`常量为`_Deprecated_gui_main.py`**

# 常见问题(FAQ)
* **什么是`SESSDATA`?**
    * **B站登陆凭证。获取方法：(B站内) 按下`F12`打开开发者工具 -> 打开`存储`栏 -> 打开`Cookie`>`https://space.bilibili.com`，在项目过滤器里可以找到`SESSDATA`键，其值就是本项目所需。**
    * **![alt text](images/image.png)**
* **此项目的可执行程序依赖有哪些？**
    * **`FFmpeg`**
    * **`Windows`/`Linux`/`Android(Termux)`**
