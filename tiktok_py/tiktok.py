from playwright.sync_api import sync_playwright
import urllib.parse
import json
from fake_useragent import UserAgent
import random
from playwright_stealth import stealth_sync


class TikTok:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        ua = UserAgent()
        self.user_agent = ua.chrome
        self.context = self.browser.new_context(user_agent=self.user_agent)
        self.page = self.context.new_page()
        stealth_sync(self.page)
        self.page.goto("https://www.tiktok.com/login/phone-or-email/email", wait_until="networkidle")
        self.language = self.page.evaluate("() => navigator.language || navigator.userLanguage")
        self.platform = self.page.evaluate("() => navigator.platform")
        self.device_id = str(random.randint(10**18, 10**19 - 1))
        self.history_len = str(random.randint(1, 10))
        self.screen_height = str(random.randint(600, 1080))
        self.screen_width = str(random.randint(800, 1920))
        self.timezone = self.page.evaluate("() => Intl.DateTimeFormat().resolvedOptions().timeZone")
        self.verify_fp = "verify_llje3d4k_v7BuITiM_H9ed_4MJ9_8dAX_zarRxLCWkrW7"

    def _generate_params(self, params: dict):
        return "?" + "&".join([f"{k}={urllib.parse.quote(v)}" for k, v in params.items()])

    def _xhr(self, url: str, params: dict = None, headers: dict = "", data: str = ""):
        if params:
            url += self._generate_params(params)
        if headers:
            headers = "\n".join([f"xhr.setRequestHeader('{k}', '{v}');" for k, v in headers.items()])
        r = self.page.evaluate(f"""
                () => {{
                    return new Promise((resolve, reject) => {{
                        let xhr = new XMLHttpRequest();
                        xhr.open('POST', '{url}');
                        {headers}
                        xhr.onload = () => resolve(xhr.responseText);
                        xhr.onerror = () => reject(xhr.statusText);
                        xhr.send('{data}');
                    }});
                }}
            """
        )
        return r

    def _fetch(self, method: str, url: str, params: dict = None, headers: dict = {}) -> str:
        if params:
            url += self._generate_params(params)
        headers = json.dumps(headers)
        r = self.page.evaluate(f"""
                () => {{
                    return new Promise((resolve, reject) => {{
                        fetch('{url}', {{ method: '{method}', headers: {headers} }})
                            .then(response => response.text())
                            .then(data => resolve(data))
                            .catch(error => reject(error.message));
                    }});
                }}
            """
        )
        return r

    def get_user_info(self, username: str):
        params = {
            "aid": "1988",
            "app_language": self.language,
            "app_name": "tiktok_web",
            "browser_language": self.language,
            "browser_name": "Mozilla",
            "browser_online": "true",
            "browser_platform": self.platform,
            "browser_version": self.user_agent,
            "channel": "tiktok_web",
            "cookie_enabled": "true",
            "device_id": self.device_id,
            "device_platform": "web_pc",
            "focus_state": "true",
            "from_page": "user",
            "history_len": self.history_len,
            "is_fullscreen": "false",
            "is_page_visible": "true",
            "language": self.language,
            "os": self.platform,
            "priority_region": "",
            "referer": "",
            "region": "MA",
            "screen_height": self.screen_height,
            "screen_width": self.screen_width,
            "tz_name": self.timezone,
            "webcast_language": self.language,
            "WebIdLastTime": "",
            "secUid": "",
            "uniqueId": username,
        }
        r = self._fetch("GET", "https://www.tiktok.com/api/user/detail/", params=params)
        print(r)

    def login(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        body = f"mix_mode=1&username=647f77647f774&password=647f7764f7764777661&aid=1459&is_sso=false&account_sdk_source=web&region=MA&language={self.language}&did={self.device_id}&fixed_mix_mode=1"
        params = {
            "multi_login": "1",
            "did": self.device_id,
            "aid": "1459",
            "account_sdk_source": "web",
            "sdk_version": "2.0.3-tiktok",
            "language": self.language,
            "verifyFp": self.verify_fp,
            "target_aid": "",
            "shark_extract": json.dumps({
                    "aid": 1459,
                    "app_name": "Tik_Tok_Login",
                    "channel": "tiktok_web",
                    "device_platform": "web_pc",
                    "device_id": self.device_id,
                    "region": "MA",
                    "priority_region": "",
                    "os": self.platform,
                    "referer": "",
                    "cookie_enabled": True,
                    "screen_width": self.screen_width,
                    "screen_height": self.screen_height,
                    "browser_language": self.language,
                    "browser_platform": self.platform,
                    "browser_name": "Mozilla",
                    "browser_version": self.user_agent,
                    "browser_online": True,
                    "verifyFp": self.verify_fp,
                    "app_language": self.language,
                    "webcast_language": self.language,
                    "tz_name": self.timezone,
                    "is_page_visible": True,
                    "focus_state": True,
                    "is_fullscreen": False,
                    "history_len": self.history_len,
                    "battery_info": None
                }
            )
        }
        r = self._xhr("https://www-useast1a.tiktok.com/passport/web/user/login/", params=params, headers=headers, data=body)
        data = json.loads(r)
        print(data)

    def follow(self, username: str):
        params = {
            "aid": "1988",
            "app_language": self.language,
            "app_name": "tiktok_web",
            "browser_language": self.language,
            "browser_name": "Mozilla",
            "browser_online": "true",
            "browser_platform": self.platform,
            "browser_version": self.user_agent,
            "channel": "tiktok_web",
            "cookie_enabled": "true",
            "device_id": self.device_id,
            "device_platform": "web_pc",
            "focus_state": "true",
            "from_page": "user",
            "history_len": self.history_len,
            "is_fullscreen": "false",
            "is_page_visible": "true",
            "language": self.language,
            "os": self.platform,
            "priority_region": "",
            "referer": "",
            "region": "MA",
            "screen_height": self.screen_height,
            "screen_width": self.screen_width,
            "tz_name": self.timezone,
            "webcast_language": self.language,
            "WebIdLastTime": "",
            "action_type": "1",
            "secUid": "",
            "uniqueId": username,
            "verifyFp": self.verify_fp
        }
        r = self._fetch("POST", "https://www.tiktok.com/api/commit/follow/user/", params=params)
        print(r)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.browser.close()
        self.playwright.stop()


if __name__ == '__main__':
    with TikTok() as tt:
        tt.login()
