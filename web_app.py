#!/usr/bin/env python3
"""
B站下载器 - Web版本
作者: 罗逸琳(Buelier)
"""

import sys
import os
import asyncio
import threading
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from config import Config
from api.bili_api import BiliAPI
from downloader.video_downloader import VideoDownloader

app = Flask(__name__)
CORS(app)

# 全局变量
config = Config()
api = BiliAPI(config.get('cookie') if config.get('cookie') else None)
downloader = VideoDownloader(config, api)
download_tasks = {}
task_counter = 0


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置"""
    return jsonify({
        'save_dir': config.get('save_dir'),
        'max_parallel': config.get('max_parallel'),
        'max_speed_mbps': config.get('max_speed_mbps'),
        'filename_format': config.get('filename_format'),
        'download_type': config.get('download_type'),
        'has_cookie': bool(config.get('cookie'))
    })


@app.route('/api/config', methods=['POST'])
def set_config():
    """设置配置"""
    data = request.json
    if 'save_dir' in data:
        config.set('save_dir', data['save_dir'])
    if 'max_parallel' in data:
        config.set('max_parallel', int(data['max_parallel']))
    if 'max_speed_mbps' in data:
        config.set('max_speed_mbps', float(data['max_speed_mbps']))
    if 'filename_format' in data:
        config.set('filename_format', data['filename_format'])
    if 'download_type' in data:
        config.set('download_type', data['download_type'])
    if 'cookie' in data:
        config.set('cookie', data['cookie'])
        api.set_cookie(data['cookie'])
    return jsonify({'success': True})


@app.route('/api/search', methods=['POST'])
def search():
    """搜索视频"""
    data = request.json
    keyword = data.get('keyword', '')
    page = data.get('page', 1)
    
    if not keyword:
        return jsonify({'error': '请输入搜索关键词'}), 400
    
    results = api.search_videos(keyword, page, 15)
    return jsonify({'results': results})


@app.route('/api/video/info', methods=['POST'])
def video_info():
    """获取视频信息"""
    data = request.json
    bvid = data.get('bvid', '')
    
    if not bvid:
        return jsonify({'error': '请输入BV号'}), 400
    
    info = api.get_video_info(bvid)
    if not info:
        return jsonify({'error': '获取视频信息失败'}), 404
    
    return jsonify({
        'bvid': info.bvid,
        'title': info.title,
        'author': info.author,
        'pubdate': info.pubdate,
        'pages': info.pages
    })


@app.route('/api/download', methods=['POST'])
def download():
    """开始下载"""
    global task_counter
    
    data = request.json
    bvid = data.get('bvid', '')
    download_type = data.get('download_type', 'audio')
    
    if not bvid:
        return jsonify({'error': '请输入BV号'}), 400
    
    task_counter += 1
    task_id = task_counter
    
    def run_download():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            download_tasks[task_id] = {'status': 'downloading', 'progress': 0}
            result = loop.run_until_complete(
                downloader.download_video(bvid, download_type)
            )
            if result:
                download_tasks[task_id] = {
                    'status': 'completed',
                    'progress': 100,
                    'file': str(result)
                }
            else:
                download_tasks[task_id] = {'status': 'failed', 'error': '下载失败'}
        except Exception as e:
            download_tasks[task_id] = {'status': 'failed', 'error': str(e)}
        finally:
            loop.close()
    
    thread = threading.Thread(target=run_download, daemon=True)
    thread.start()
    
    return jsonify({'task_id': task_id})


@app.route('/api/download/status/<int:task_id>', methods=['GET'])
def download_status(task_id):
    """获取下载状态"""
    task = download_tasks.get(task_id, {'status': 'not_found'})
    return jsonify(task)


@app.route('/api/favorites', methods=['POST'])
def download_favorites():
    """下载收藏夹"""
    global task_counter
    
    data = request.json
    fid = data.get('fid', '')
    is_private = data.get('is_private', False)
    download_type = data.get('download_type', 'audio')
    
    if not fid:
        return jsonify({'error': '请输入收藏夹ID'}), 400
    
    task_counter += 1
    task_id = task_counter
    
    def run_fav_download():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            items = api.get_favorites(int(fid), is_private)
            if not items:
                download_tasks[task_id] = {'status': 'failed', 'error': '未获取到收藏夹内容'}
                return
            
            total = len(items)
            download_tasks[task_id] = {'status': 'downloading', 'progress': 0, 'total': total}
            
            success = 0
            for i, item in enumerate(items):
                bvid = item.get('bvid')
                if bvid:
                    result = loop.run_until_complete(
                        downloader.download_video(bvid, download_type)
                    )
                    if result:
                        success += 1
                download_tasks[task_id]['progress'] = int((i + 1) / total * 100)
            
            download_tasks[task_id] = {
                'status': 'completed',
                'progress': 100,
                'success': success,
                'total': total
            }
        except Exception as e:
            download_tasks[task_id] = {'status': 'failed', 'error': str(e)}
        finally:
            loop.close()
    
    thread = threading.Thread(target=run_fav_download, daemon=True)
    thread.start()
    
    return jsonify({'task_id': task_id})


@app.route('/api/batch', methods=['POST'])
def batch_download():
    """批量下载"""
    global task_counter
    
    data = request.json
    bvids = data.get('bvids', [])
    download_type = data.get('download_type', 'audio')
    
    if not bvids:
        return jsonify({'error': '请提供BV号列表'}), 400
    
    task_counter += 1
    task_id = task_counter
    
    def run_batch():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            total = len(bvids)
            download_tasks[task_id] = {'status': 'downloading', 'progress': 0, 'total': total}
            
            success = 0
            for i, bvid in enumerate(bvids):
                result = loop.run_until_complete(
                    downloader.download_video(bvid, download_type)
                )
                if result:
                    success += 1
                download_tasks[task_id]['progress'] = int((i + 1) / total * 100)
            
            download_tasks[task_id] = {
                'status': 'completed',
                'progress': 100,
                'success': success,
                'total': total
            }
        except Exception as e:
            download_tasks[task_id] = {'status': 'failed', 'error': str(e)}
        finally:
            loop.close()
    
    thread = threading.Thread(target=run_batch, daemon=True)
    thread.start()
    
    return jsonify({'task_id': task_id})


if __name__ == '__main__':
    # 创建模板目录
    template_dir = Path(__file__).parent / 'templates'
    template_dir.mkdir(exist_ok=True)
    
    print("=" * 50)
    print("B站下载器 - Web版本")
    print("=" * 50)
    print(f"访问地址: http://127.0.0.1:5000")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)