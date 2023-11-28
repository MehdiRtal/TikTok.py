from playwright.sync_api import sync_playwright
import urllib.parse
import json
from fake_useragent import UserAgent
import random
from playwright_stealth import stealth_sync


class TikTok:
    def __init__(self, headless: bool = False, proxy: str = None):
        self.playwright = sync_playwright().start()
        tmp_proxy = None
        if proxy:
            tmp_proxy = {
                "server": f"http://{proxy}",
            }
            if "@" in proxy:
                tmp_proxy["server"] = f"http://{proxy.split('@')[1]}"
                tmp_proxy["username"] = proxy.split("@")[0].split(":")[0]
                tmp_proxy["password"] = proxy.split("@")[0].split(":")[1]
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            proxy=tmp_proxy
        )
        ua = UserAgent()
        self.user_agent = ua.chrome
        self.context = self.browser.new_context(user_agent=self.user_agent)
        self.page = self.context.new_page()
        stealth_sync(self.page)
        self.page.goto("https://www.tiktok.com/")
        self.language = self.page.evaluate("() => navigator.language || navigator.userLanguage")
        self.platform = self.page.evaluate("() => navigator.platform")
        self.device_id = str(random.randint(10**18, 10**19 - 1))
        self.history_len = str(random.randint(1, 10))
        self.screen_height = str(random.randint(600, 1080))
        self.screen_width = str(random.randint(800, 1920))
        self.timezone = self.page.evaluate("() => Intl.DateTimeFormat().resolvedOptions().timeZone")
        self.verify_fp = ""

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

    def login(self, session: dict = None):
        if session:
            self.page.context.add_cookies(session)

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

    def call(self, number: str, country_code: str):
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "codeChannel": 1,
            "target": number,
            "country": country_code,
            "isCipher": False
        })
        r = self._xhr("https://www.tiktok.com/api/ba/business/suite/verification/contact/send/?lang=ar&language=ar", headers=headers, data=data)
        print(r)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.browser.close()
        self.playwright.stop()
