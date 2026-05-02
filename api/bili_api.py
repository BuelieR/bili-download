"""
B站API封装模块
"""

import re
import time
import requests
from typing import Optional, List, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from models.video_info import VideoInfo


class BiliAPI:
    """B站API接口类"""
    
    def __init__(self, cookie: Optional[str] = None):
        self.session = requests.Session()
        
        # 重试机制
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Referer": "https://www.bilibili.com",
            "Accept-Language": "zh-CN,zh;q=0.9"
        })
        if cookie:
            self.set_cookie(cookie)
    
    def set_cookie(self, cookie: str):
        """设置SESSDATA Cookie"""
        # 清除可能存在的旧cookie
        self.session.cookies.clear()
        # 设置新的SESSDATA
        self.session.cookies.set("SESSDATA", cookie, domain=".bilibili.com")
        # 辅助cookie
        self.session.cookies.set("DedeUserID", "", domain=".bilibili.com")
        self.session.cookies.set("bili_jct", "", domain=".bilibili.com")
        
        # 更新headers中的Referer
        self.session.headers.update({
            "Referer": "https://www.bilibili.com",
            "Origin": "https://www.bilibili.com"
        })
        
        print("Cookie已设置")
    
    def get_bvid_from_url(self, url_or_bvid: str) -> Optional[str]:
        """从URL或字符串中提取BV号"""
        # BV号
        if re.match(r'^BV[a-zA-Z0-9]{10}$', url_or_bvid):
            return url_or_bvid
        
        # URL提取
        patterns = [
            r'BV([a-zA-Z0-9]{10})',
            r'bilibili\.com/video/(BV[a-zA-Z0-9]+)',
            r'bilibili\.com/video/(av\\d+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url_or_bvid)
            if match:
                return match.group(1) if 'BV' in match.group(1) else match.group(0)
        return None
    
    def get_video_info(self, bvid: str, retry: int = 3) -> Optional[VideoInfo]:
        """获取视频信息"""
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        
        for attempt in range(retry):
            try:
                resp = self.session.get(url, timeout=10)
                data = resp.json()
                
                if data['code'] != 0:
                    print(f"API错误: {data.get('message', '未知错误')}")
                    return None
                
                info = data['data']
                return VideoInfo(
                    bvid=bvid,
                    title=info['title'],
                    author=info['owner']['name'],
                    pubdate=info['pubdate'],
                    pages=info.get('videos', 1),
                    cid=info['cid']
                )
            except requests.exceptions.ConnectionError as e:
                print(f"连接失败 (尝试 {attempt + 1}/{retry}): {e}")
                if attempt < retry - 1:
                    time.sleep(2)
                else:
                    print("网络连接失败，请检查网络")
                    return None
            except Exception as e:
                print(f"获取视频信息失败: {e}")
                return None
        
        return None
    
    def get_download_url(self, bvid: str, cid: int, quality: int = 80) -> Dict[str, Any]:
        """获取视频/音频下载链接"""
        url = "https://api.bilibili.com/x/player/playurl"
        params = {
            "bvid": bvid,
            "cid": cid,
            "qn": quality,
            "fnver": 0,
            "fnval": 4048,  
            # 启用DASH+无损音频
            "fourk": 1
        }
        
        try:
            resp = self.session.get(url, params=params, timeout=10)
            return resp.json().get('data', {})
        except Exception as e:
            print(f"获取下载链接失败: {e}")
            return {}
    
    def search_videos(self, keyword: str, page: int = 1, page_size: int = 15) -> List[Dict]:
        """搜索视频"""
        url = "https://api.bilibili.com/x/web-interface/search/type"
        params = {
            "search_type": "video",
            "keyword": keyword,
            "page": page,
            "page_size": page_size
        }
        
        try:
            # 完整的请求头
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://www.bilibili.com/",
                "Origin": "https://www.bilibili.com",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site",
                "Connection": "keep-alive"
            }
            
            # 添加cookie（如果有）
            if self.session.cookies.get("SESSDATA"):
                headers["Cookie"] = f"SESSDATA={self.session.cookies.get('SESSDATA')}"
            
            # requests直接请求
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            # 检查响应状态
            if response.status_code != 200:
                print(f"搜索请求失败: HTTP {response.status_code}")
                if response.status_code == 412:
                    print("提示：B站API需要更完整的请求头或cookie")
                return []
            
            # 检查响应内容
            if not response.text:
                print("搜索响应为空")
                return []
            
            # 解析JSON
            try:
                data = response.json()
            except Exception as e:
                print(f"JSON解析失败: {e}")
                print(f"响应内容: {response.text[:200]}")
                return []
            
            if data['code'] != 0:
                print(f"搜索API错误: {data.get('message', '未知错误')}")
                return []
            
            results = []
            for item in data.get('data', {}).get('result', []):
                # 清理标题标签
                title = item.get('title', '')
                import re
                title = re.sub(r'<em class="keyword">', '', title)
                title = re.sub(r'</em>', '', title)
                
                results.append({
                    "title": title,
                    "author": item.get('author', '未知'),
                    "bvid": item.get('bvid', ''),
                    "play": item.get('play', 0),
                    "duration": item.get('duration', ''),
                    "pubdate": item.get('pubdate', '')
                })
            return results
            
        except requests.exceptions.Timeout:
            print("搜索请求超时")
            return []
        except requests.exceptions.ConnectionError as e:
            print(f"连接错误: {e}")
            return []
        except Exception as e:
            print(f"搜索失败: {e}")
            return []

    def search_videos_v2(self, keyword: str, page: int = 1, page_size: int = 15) -> List[Dict]:
        """备用搜索API"""
        url = "https://api.bilibili.com/x/web-interface/wbi/search/type"
        params = {
            "search_type": "video",
            "keyword": keyword,
            "page": page,
            "page_size": page_size
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://search.bilibili.com/",
            "Origin": "https://search.bilibili.com"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            
            if data['code'] != 0:
                return []
            
            results = []
            for item in data.get('data', {}).get('result', []):
                import re
                title = re.sub(r'<em class="keyword">', '', item.get('title', ''))
                title = re.sub(r'</em>', '', title)
                
                results.append({
                    "title": title,
                    "author": item.get('author', '未知'),
                    "bvid": item.get('bvid', ''),
                    "play": item.get('play', 0),
                    "duration": item.get('duration', '')
                })
            return results
        except Exception as e:
            print(f"备用搜索失败: {e}")
            return []

    def get_favorites(self, fid: int, is_private: bool = False, page_size: int = 20) -> List[Dict]:
        """获取收藏夹内容"""
        all_items = []
        page = 1
        total_count = None
        
        while True:
            url = "https://api.bilibili.com/x/v3/fav/resource/list"
            params = {
                "media_id": fid,
                "pn": page,
                "ps": page_size,
                "platform": "web",
                "ts": int(time.time())
            }
            
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": f"https://space.bilibili.com/",
                    "Origin": "https://www.bilibili.com"
                }
                
                resp = self.session.get(url, params=params, headers=headers, timeout=10)
                data = resp.json()
                
                if data['code'] != 0:
                    print(f"API错误: {data.get('message', '未知错误')}")
                    break
                
                # 获取总数（第一次请求时）
                if total_count is None:
                    info = data.get('data', {}).get('info', {})
                    total_count = info.get('media_count', 0)
                    if total_count == 0:
                        total_count = len(data.get('data', {}).get('medias', []))
                    print(f"收藏夹共有 {total_count} 个视频")
                
                medias = data.get('data', {}).get('medias', [])
                if not medias:
                    break
                
                # 提取视频信息
                for item in medias:
                    if 'bvid' in item:
                        all_items.append({
                            'bvid': item.get('bvid'),
                            'title': item.get('title'),
                            'author': item.get('upper', {}).get('name', '未知'),
                            'cid': item.get('cid', 0),
                            'page': item.get('page', 1)
                        })
                
                print(f"已获取第 {page} 页，共 {len(medias)} 个视频，累计 {len(all_items)}/{total_count if total_count > 0 else '?'}")
                
                # 检查是否还有更多
                if len(medias) < page_size:
                    break
                if total_count > 0 and len(all_items) >= total_count:
                    break
                
                page += 1
                
            except Exception as e:
                print(f"获取收藏夹异常: {e}")
                break
        
        return all_items
    
    def get_page_info(self, bvid: str, page: int) -> Optional[Dict]:
        """获取合集分页信息"""
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        
        try:
            resp = self.session.get(url, timeout=10)
            data = resp.json()
            
            if data['code'] != 0:
                return None
            
            pages = data['data'].get('pages', [])
            if page <= len(pages):
                return pages[page - 1]
            return None
        except Exception as e:
            print(f"获取分页信息失败: {e}")
            return None