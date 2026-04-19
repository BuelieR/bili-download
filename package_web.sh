#!/bin/bash

set -e

APP_NAME="bili-downloader-web"
VERSION="1.0.0"
AUTHOR="Buelier"
MAIN_FILE="web_app.py"

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

if [ ! -f "settings.json" ]; then
    echo -e "${YELLOW}创建默认 settings.json...${NC}"
    cat > settings.json << 'EOF'
{
  "save_dir": "$HOME/BiliDownloads",
  "max_parallel": 3,
  "max_speed_mbps": 0,
  "filename_format": "${video_name}_AUTHOR_${video_author}",
  "download_type": "audio",
  "cookie": "",
  "quality": 80,
  "auto_retry": 3,
  "timeout": 30
}
EOF
fi

echo -e "${YELLOW}使用 PyInstaller 打包...${NC}"
pyinstaller --onefile \
    --name "${APP_NAME}" \
    --add-data "templates:templates" \
    --add-data "settings.json:." \
    --hidden-import "asyncio" \
    --hidden-import "aiohttp" \
    --hidden-import "aiofiles" \
    --hidden-import "requests" \
    --hidden-import "flask" \
    ${MAIN_FILE}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PyInstaller 打包成功${NC}"
else
    echo -e "${RED}✗ PyInstaller 打包失败${NC}"
    exit 1
fi

echo -e "${YELLOW}打包为 DEB 文件...${NC}"

DEB_NAME="${APP_NAME}_${VERSION}_all"
DEB_DIR="package/${DEB_NAME}"

mkdir -p ${DEB_DIR}/DEBIAN
mkdir -p ${DEB_DIR}/usr/local/bin
mkdir -p ${DEB_DIR}/usr/share/${APP_NAME}/templates
mkdir -p ${DEB_DIR}/usr/share/applications
mkdir -p ${DEB_DIR}/usr/share/icons/hicolor/128x128/apps
mkdir -p ${DEB_DIR}/etc/${APP_NAME}

cp dist/${APP_NAME} ${DEB_DIR}/usr/local/bin/

cp -r templates/* ${DEB_DIR}/usr/share/${APP_NAME}/templates/ 2>/dev/null || true

cp settings.json ${DEB_DIR}/etc/${APP_NAME}/settings.json.default

cat > ${DEB_DIR}/DEBIAN/control << EOF
Package: ${APP_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: all
Depends: ffmpeg
Maintainer: ${AUTHOR}
Description: B站视频和音频下载工具
 功能特性:
  • 支持视频/音频下载
  • 支持收藏夹批量下载
  • 支持多线程并行下载
  • 可自定义文件名格式
 .
 使用命令: bili-downloader
EOF

cat > ${DEB_DIR}/DEBIAN/postinst << 'EOF'
#!/bin/bash
set -e

mkdir -p /usr/share/bili-downloader
mkdir -p /etc/bili-downloader

USER_CONFIG="$HOME/.config/bili-downloader/settings.json"
if [ ! -f "$USER_CONFIG" ] && [ -f /etc/bili-downloader/settings.json.default ]; then
    mkdir -p "$(dirname "$USER_CONFIG")"
    cp /etc/bili-downloader/settings.json.default "$USER_CONFIG"
    
    sed -i "s|\$HOME|$HOME|g" "$USER_CONFIG"
fi

chmod 755 /usr/local/bin/bili-downloader

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database
fi

echo ""
echo "=========================================="
echo "B站下载器安装完成！"
echo "=========================================="
echo "运行命令: bili-downloader"
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
Comment=B站视频和音频下载工具
Exec=/usr/local/bin/${APP_NAME}
Icon=/usr/share/icons/hicolor/128x128/apps/${APP_NAME}.png
Terminal=true
Type=Application
Categories=AudioVideo;Network;
EOF

cat > ${DEB_DIR}/usr/share/icons/hicolor/128x128/apps/${APP_NAME}.png << 'EOF'
iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAIzSURBVHic7d0/TuNAGMbxnzG7m2yUAgqKkCgoKBBSKop0O8EJOAFH4AgcgSNwBI5A5wihVKSlQEEoKFDYxI7tL8XISWRnHGK/z5OkHPLsvPb4J0sIIYQQQgghhBBCiK+yS5H+3Fxc/LVJkr/yvD9q2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRK2bbtt2/YoSRL29vY+kiRhn883GIZhx3EcpmnapmlKgiAIIYQQQgghhBDiv+oJ7/lSFZ53MdoAAAAASUVORK5CYII=
EOF

cd package
dpkg-deb --build ${DEB_NAME}
if [ $? -eq 0 ]; then
    mv ${DEB_NAME}.deb ..
    echo -e "${GREEN}✓ DEB 包创建成功${NC}"
else
    echo -e "${RED}✗ DEB 包创建失败${NC}"
    exit 1
fi
cd ..

echo -e "${YELLOW}打包为 TGZ 文件...${NC}"

TGZ_NAME="${APP_NAME}-${VERSION}.tar.gz"
TGZ_DIR="${APP_NAME}-${VERSION}"

rm -rf ${TGZ_DIR}
mkdir -p ${TGZ_DIR}
mkdir -p ${TGZ_DIR}/templates

cp dist/${APP_NAME} ${TGZ_DIR}/
cp -r templates/* ${TGZ_DIR}/templates/ 2>/dev/null || true
cp settings.json ${TGZ_DIR}/ 2>/dev/null || true

cat > ${TGZ_DIR}/run.sh << 'EOF'
#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="${SCRIPT_DIR}:$PATH"

CONFIG_DIR="$HOME/.config/bili-downloader"
mkdir -p "$CONFIG_DIR"

if [ ! -f "$CONFIG_DIR/settings.json" ] && [ -f "$SCRIPT_DIR/settings.json" ]; then
    cp "$SCRIPT_DIR/settings.json" "$CONFIG_DIR/"
    sed -i "s|\$HOME|$HOME|g" "$CONFIG_DIR/settings.json"
fi

if ! command -v ffmpeg &> /dev/null; then
    echo "警告: FFmpeg 未安装，音频转换功能可能不可用"
    echo "请安装: sudo apt install ffmpeg"
fi

"${SCRIPT_DIR}/bili-downloader"
EOF

chmod +x ${TGZ_DIR}/run.sh
chmod +x ${TGZ_DIR}/bili-downloader

cat > ${TGZ_DIR}/INSTALL.txt << EOF
B站下载器安装说明
==================

快速开始:
1. 解压: tar -xzf ${TGZ_NAME}
2. 运行: cd ${APP_NAME}-${VERSION} && ./run.sh

安装到系统:
sudo cp bili-downloader /usr/local/bin/
sudo cp -r templates /usr/share/bili-downloader/

依赖要求:
- FFmpeg: sudo apt install ffmpeg

配置文件:
~/.config/bili-downloader/settings.json

卸载:
sudo rm /usr/local/bin/bili-downloader
rm -rf ~/.config/bili-downloader
EOF

tar -czf ${TGZ_NAME} ${TGZ_DIR}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ TGZ 包创建成功: ${TGZ_NAME}${NC}"
else
    echo -e "${RED}✗ TGZ 包创建失败${NC}"
fi

rm -rf ${TGZ_DIR}
rm -rf package

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}打包完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "生成的文件:"
ls -lh *.deb *.tar.gz 2>/dev/null
echo -e "${GREEN}========================================${NC}"
