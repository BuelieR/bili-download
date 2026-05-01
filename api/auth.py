"""
登录认证模块
"""

import requests
from typing import Optional


class BiliAuth:
    """B站认证类"""
    
    def __init__(self, session: requests.Session):
        self.session = session
        
    def set_cookie(self, cookie: str):
        """设置Cookie"""
        self.session.cookies.set("SESSDATA", cookie)

    def set_sessdata(self, sessdata: str) -> None:
        """设置SESSDATA Cookie"""
        self.session.cookies.set("SESSDATA", sessdata)
        self.session.cookies.set("DedeUserID", "", domain=".bilibili.com")
    
    def get_sessdata(self) -> Optional[str]:
        """获取当前的SESSDATA"""
        return self.session.cookies.get("SESSDATA")
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        try:
            resp = self.session.get("https://api.bilibili.com/x/web-interface/nav")
            data = resp.json()
            return data.get('code') == 0 and data.get('data', {}).get('isLogin', False)
        except:
            return False
    
    def get_user_info(self) -> Optional[dict]:
        """获取当前登录用户信息"""
        try:
            resp = self.session.get("https://api.bilibili.com/x/web-interface/nav")
            data = resp.json()
            if data.get('code') == 0:
                return data.get('data', {})
        except:
            pass
        return None