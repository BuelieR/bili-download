#!/bin/bash

set -e

umask 022

APP_NAME="bili-downloader"
VERSION="1.0.1"
AUTHOR="BuelieR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}B站下载器打包工具 v${VERSION}${NC}"
echo -e "${GREEN}========================================${NC}"

if [ ! -d "venv" ]; then
    echo -e "${RED}错误: 虚拟环境不存在，请先创建虚拟环境${NC}"
    exit 1
fi

source venv/bin/activate

echo -e "${YELLOW}清理旧的构建文件...${NC}"
rm -rf build dist *.spec
rm -rf *.deb *.tar.gz package

echo -e "${YELLOW}检查模板目录...${NC}"
if [ ! -d "templates" ]; then
    echo -e "${YELLOW}创建 templates 目录...${NC}"
    mkdir -p templates
    cat > templates/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head><title>B站下载器</title></head>
<body>
<h1>B站下载器</h1>
<p>请确保 Flask 已安装并正确配置</p>
</body>
</html>
EOF
fi

echo -e "${YELLOW}打包 CLI 版本...${NC}"
pyinstaller --onefile \
    --name "${APP_NAME}" \
    --add-data "templates:templates" \
    --hidden-import "asyncio" \
    --hidden-import "aiohttp" \
    --hidden-import "aiofiles" \
    --hidden-import "requests" \
    --hidden-import "flask" \
    --hidden-import "pydantic" \
    cli.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ CLI 版本打包成功${NC}"
else
    echo -e "${RED}✗ CLI 版本打包失败${NC}"
    exit 1
fi

echo -e "${YELLOW}打包 GUI 版本...${NC}"

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo -e "${YELLOW}切换到 gui_version 分支...${NC}"
git checkout gui_version

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 无法切换到 gui_version 分支${NC}"
    exit 1
fi

pyinstaller --onefile \
    --name "${APP_NAME}-gui" \
    --add-data "templates:templates" \
    --add-data "gui:gui" \
    --hidden-import "asyncio" \
    --hidden-import "aiohttp" \
    --hidden-import "aiofiles" \
    --hidden-import "requests" \
    --hidden-import "pydantic" \
    --hidden-import "customtkinter" \
    --hidden-import "tkinter" \
    gui_main.py

GUI_SUCCESS=$?

echo -e "${YELLOW}切换回 ${CURRENT_BRANCH} 分支...${NC}"
git checkout ${CURRENT_BRANCH}

if [ $GUI_SUCCESS -eq 0 ]; then
    echo -e "${GREEN}✓ GUI 版本打包成功${NC}"
else
    echo -e "${RED}✗ GUI 版本打包失败${NC}"
    exit 1
fi

echo -e "${YELLOW}打包为 DEB 文件...${NC}"

DEB_NAME="${APP_NAME}_${VERSION}_all"
DEB_DIR="package/${DEB_NAME}"

rm -rf package
mkdir -p ${DEB_DIR}/DEBIAN
mkdir -p ${DEB_DIR}/usr/local/bin
mkdir -p ${DEB_DIR}/usr/share/${APP_NAME}/templates
mkdir -p ${DEB_DIR}/usr/share/applications
mkdir -p ${DEB_DIR}/usr/share/icons/hicolor/128x128/apps
mkdir -p ${DEB_DIR}/etc/${APP_NAME}

cp dist/${APP_NAME} ${DEB_DIR}/usr/local/bin/
cp dist/${APP_NAME}-gui ${DEB_DIR}/usr/local/bin/
chmod 755 ${DEB_DIR}/usr/local/bin/${APP_NAME}
chmod 755 ${DEB_DIR}/usr/local/bin/${APP_NAME}-gui

if [ -d "templates" ]; then
    cp -r templates/* ${DEB_DIR}/usr/share/${APP_NAME}/templates/ 2>/dev/null || true
    find ${DEB_DIR}/usr/share/${APP_NAME}/templates -type f -exec chmod 644 {} \; 2>/dev/null || true
fi

cat > ${DEB_DIR}/DEBIAN/control << EOF
Package: ${APP_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: all
Depends: ffmpeg, python3-tk
Maintainer: ${AUTHOR}
Description: B站视频和音频下载工具
 功能特性:
  • CLI和GUI双版本
  • 支持视频/音频下载
  • 支持收藏夹批量下载
  • 支持多线程并行下载
  • 可自定义文件名格式
  • 支持明暗主题切换
 .
 CLI命令: bili-downloader
 GUI命令: bili-downloader-gui
EOF

chmod 644 ${DEB_DIR}/DEBIAN/control

cat > ${DEB_DIR}/DEBIAN/postinst << 'EOF'
#!/bin/bash
set -e

mkdir -p /usr/share/bili-downloader
mkdir -p /etc/bili-downloader

chmod 755 /usr/local/bin/bili-downloader
chmod 755 /usr/local/bin/bili-downloader-gui

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database
fi

echo ""
echo "=========================================="
echo "B站下载器安装完成！"
echo "=========================================="
echo "CLI运行: bili-downloader"
echo "GUI运行: bili-downloader-gui"
echo "配置文件: ~/.config/bili-downloader/settings.json"
echo "=========================================="
echo ""

exit 0
EOF

chmod 755 ${DEB_DIR}/DEBIAN/postinst

cat > ${DEB_DIR}/DEBIAN/prerm << 'EOF'
#!/bin/bash
set -e

echo "正在卸载 B站下载器..."

read -p "是否删除配置文件? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$HOME/.config/bili-downloader"
    echo "已删除配置文件"
else
    echo "保留配置文件: ~/.config/bili-downloader"
fi

exit 0
EOF

chmod 755 ${DEB_DIR}/DEBIAN/prerm

cat > ${DEB_DIR}/usr/share/applications/${APP_NAME}.desktop << EOF
[Desktop Entry]
Version=${VERSION}
Name=B站下载器
Name[zh_CN]=B站下载器
Comment=B站视频和音频下载工具 (CLI)
Exec=/usr/local/bin/${APP_NAME}
Icon=/usr/share/icons/hicolor/128x128/apps/${APP_NAME}.png
Terminal=true
Type=Application
Categories=AudioVideo;Network;Utility;
EOF

chmod 644 ${DEB_DIR}/usr/share/applications/${APP_NAME}.desktop

cat > ${DEB_DIR}/usr/share/applications/${APP_NAME}-gui.desktop << EOF
[Desktop Entry]
Version=${VERSION}
Name=B站下载器 GUI
Name[zh_CN]=B站下载器 GUI
Comment=B站视频和音频下载工具 (图形界面)
Exec=/usr/local/bin/${APP_NAME}-gui
Icon=/usr/share/icons/hicolor/128x128/apps/${APP_NAME}.png
Terminal=false
Type=Application
Categories=AudioVideo;Network;Utility;
EOF

chmod 644 ${DEB_DIR}/usr/share/applications/${APP_NAME}-gui.desktop

cat > ${DEB_DIR}/usr/share/icons/hicolor/128x128/apps/${APP_NAME}.png << 'EOF'
iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIzSURBVHic7d0/TuNAGMbxnzG7m2yUAgqKkCgoKBBSKop0O8EJOAFH4AgcgSNwBI5A5wihVKSlQEEoKFDYxI7tL8XISWRnHGK/z5OkHPLsvPb4J0sIIYQQQgghhBBCiK+yS5H+3Fxc/LVJkr/yvD9q2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRL29vY+kiRhn883GIZhx3EcpmnapmlKgiAIIYQQQgghhBDiv+oJ7/lSFZ53MdoAAAAASUVORK5CYII=
EOF

chmod 644 ${DEB_DIR}/usr/share/icons/hicolor/128x128/apps/${APP_NAME}.png

cd package
fakeroot bash -c "
find ${DEB_NAME} -type d -exec chmod 755 {} \;
find ${DEB_NAME} -type f -exec chmod 644 {} \;
chmod 755 ${DEB_NAME}/DEBIAN/postinst
chmod 755 ${DEB_NAME}/DEBIAN/prerm
chmod 755 ${DEB_NAME}/usr/local/bin/${APP_NAME}
chmod 755 ${DEB_NAME}/usr/local/bin/${APP_NAME}-gui
chmod 755 ${DEB_NAME}/DEBIAN
dpkg-deb --build ${DEB_NAME}
"
if [ $? -eq 0 ]; then
    mv ${DEB_NAME}.deb ..
    echo -e "${GREEN}✓ DEB 包创建成功${NC}"
else
    echo -e "${RED}✗ DEB 包创建失败${NC}"
    exit 1
fi
cd ..

echo -e "${YELLOW}打包为 TGZ 文件 (CLI)...${NC}"

TGZ_NAME="${APP_NAME}-${VERSION}-cli.tar.gz"
TGZ_DIR="${APP_NAME}-${VERSION}-cli"

rm -rf ${TGZ_DIR}
mkdir -p ${TGZ_DIR}
mkdir -p ${TGZ_DIR}/templates

cp dist/${APP_NAME} ${TGZ_DIR}/
cp -r templates/* ${TGZ_DIR}/templates/ 2>/dev/null || true

cat > ${TGZ_DIR}/run.sh << 'EOF'
#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="${SCRIPT_DIR}:$PATH"

CONFIG_DIR="$HOME/.config/bili-downloader"
mkdir -p "$CONFIG_DIR"

if ! command -v ffmpeg &> /dev/null; then
    echo "警告: FFmpeg 未安装，音频转换功能可能不可用"
    echo "请安装: sudo apt install ffmpeg"
fi

"${SCRIPT_DIR}/bili-downloader"
EOF

chmod +x ${TGZ_DIR}/run.sh
chmod +x ${TGZ_DIR}/bili-downloader

cat > ${TGZ_DIR}/INSTALL.txt << EOF
B站下载器 CLI 版本 - 安装说明
==============================

快速开始:
1. 解压: tar -xzf ${TGZ_NAME}
2. 运行: cd ${TGZ_DIR} && ./run.sh

安装到系统:
sudo cp bili-downloader /usr/local/bin/
sudo cp -r templates /usr/share/bili-downloader/

依赖要求:
- FFmpeg: sudo apt install ffmpeg

配置文件:
~/.config/bili-downloader/settings.json (首次运行自动创建)

卸载:
sudo rm /usr/local/bin/bili-downloader
rm -rf ~/.config/bili-downloader
EOF

tar -czf ${TGZ_NAME} ${TGZ_DIR}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ CLI TGZ 包创建成功: ${TGZ_NAME}${NC}"
else
    echo -e "${RED}✗ CLI TGZ 包创建失败${NC}"
fi

echo -e "${YELLOW}打包为 TGZ 文件 (GUI)...${NC}"

TGZ_NAME_GUI="${APP_NAME}-${VERSION}-gui.tar.gz"
TGZ_DIR_GUI="${APP_NAME}-${VERSION}-gui"

rm -rf ${TGZ_DIR_GUI}
mkdir -p ${TGZ_DIR_GUI}
mkdir -p ${TGZ_DIR_GUI}/templates
mkdir -p ${TGZ_DIR_GUI}/gui

cp dist/${APP_NAME}-gui ${TGZ_DIR_GUI}/
cp -r templates/* ${TGZ_DIR_GUI}/templates/ 2>/dev/null || true
cp -r gui/* ${TGZ_DIR_GUI}/gui/ 2>/dev/null || true

cat > ${TGZ_DIR_GUI}/run.sh << 'EOF'
#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="${SCRIPT_DIR}:$PATH"

CONFIG_DIR="$HOME/.config/bili-downloader"
mkdir -p "$CONFIG_DIR"

if ! command -v ffmpeg &> /dev/null; then
    echo "警告: FFmpeg 未安装，音频转换功能可能不可用"
    echo "请安装: sudo apt install ffmpeg"
fi

if ! command -v python3-tk &> /dev/null; then
    echo "警告: Python3 Tkinter 未安装，GUI可能无法正常运行"
    echo "请安装: sudo apt install python3-tk"
fi

"${SCRIPT_DIR}/bili-downloader-gui"
EOF

chmod +x ${TGZ_DIR_GUI}/run.sh
chmod +x ${TGZ_DIR_GUI}/bili-downloader-gui

cat > ${TGZ_DIR_GUI}/INSTALL.txt << EOF
B站下载器 GUI 版本 - 安装说明
==============================

快速开始:
1. 解压: tar -xzf ${TGZ_NAME_GUI}
2. 运行: cd ${TGZ_DIR_GUI} && ./run.sh

安装到系统:
sudo cp bili-downloader-gui /usr/local/bin/
sudo cp -r templates /usr/share/bili-downloader/
sudo cp -r gui /usr/share/bili-downloader/

依赖要求:
- FFmpeg: sudo apt install ffmpeg
- Python3 Tkinter: sudo apt install python3-tk

配置文件:
~/.config/bili-downloader/settings.json (首次运行自动创建)

卸载:
sudo rm /usr/local/bin/bili-downloader-gui
rm -rf ~/.config/bili-downloader
EOF

tar -czf ${TGZ_NAME_GUI} ${TGZ_DIR_GUI}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ GUI TGZ 包创建成功: ${TGZ_NAME_GUI}${NC}"
else
    echo -e "${RED}✗ GUI TGZ 包创建失败${NC}"
fi

rm -rf ${TGZ_DIR}
rm -rf ${TGZ_DIR_GUI}
rm -rf package

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}打包完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "生成的文件:"
ls -lh *.deb *.tar.gz 2>/dev/null
echo -e "${GREEN}========================================${NC}"