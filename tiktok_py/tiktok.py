from playwright.sync_api import sync_playwright
import urllib.parse
import json
from fake_useragent import UserAgent
import random
from playwright_stealth import stealth_sync

from omocaptcha_py import OMOCaptcha


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
            devtools=True,
            headless=headless,
            proxy=tmp_proxy
        )
        ua = UserAgent()
        self.user_agent = ua.chrome
        self.context = self.browser.new_context(user_agent=self.user_agent)
        self.page = self.context.new_page()
        stealth_sync(self.page)
        self.language = self.page.evaluate("() => navigator.language || navigator.userLanguage")
        self.platform = self.page.evaluate("() => navigator.platform")
        self.device_id = str(random.randint(10**18, 10**19 - 1))
        self.history_len = str(random.randint(1, 10))
        self.screen_height = str(random.randint(600, 1080))
        self.screen_width = str(random.randint(800, 1920))
        self.timezone = self.page.evaluate("() => Intl.DateTimeFormat().resolvedOptions().timeZone")
        self.verify_fp = None

    def _generate_params(self, params: dict):
        return "?" + "&".join([f"{k}={urllib.parse.quote(v)}" for k, v in params.items()])

    def _xhr(self, method: str, url: str, params: dict = None, headers: dict = "", data: str = ""):
        if params:
            url += self._generate_params(params)
        if headers:
            headers = "\n".join([f"xhr.setRequestHeader('{k}', '{v}');" for k, v in headers.items()])
        r = self.page.evaluate(f"""
            () => {{
                return new Promise((resolve, reject) => {{
                    let xhr = new XMLHttpRequest();
                    xhr.open('{method}', '{url}');
                    {headers}
                    xhr.onload = () => resolve(xhr.responseText);
                    xhr.onerror = () => reject(xhr.statusText);
                    xhr.send('{data}');
                }});
            }}
        """)
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

    def login(self, username: str = None, password: str = None, session: dict = None):
        self.page.goto("https://www.tiktok.com/login/phone-or-email/email", wait_until="networkidle")
        if session:
            self.context.add_cookies(session)
            for cookies in self.context.cookies():
                if cookies["name"] == "s_v_web_id":
                    self.verify_fp = cookies["value"]
        elif username and password:
            self.context.add_cookies([{"name": "s_v_web_id", "value": "verify_lpk89oqr_qU1by6Lt_AC6b_460F_A0vc_2vvSOYC4H1Zz", "domain": ".tiktok.com", "path": "/"}])
            self.verify_fp = "verify_lpk89oqr_qU1by6Lt_AC6b_460F_A0vc_2vvSOYC4H1Zz"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            body = f"mix_mode=1&username={username}&password={password}&aid=1459&is_sso=false&account_sdk_source=web&region=MA&language={self.language}&did={self.device_id}&fixed_mix_mode=1"
            params = {
                "multi_login": "1",
                "did": self.device_id,
                "aid": "1459",
                "account_sdk_source": "web",
                "sdk_version": "2.0.3-tiktok",
                "language": self.language,
                "verifyFp": self.verify_fp,
                "target_aid": "",
                "fp": self.verify_fp,
                "shark_extra": json.dumps({
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
            for _ in range(2):
                r = self._xhr("POST", "https://www-useast1a.tiktok.com/passport/web/user/login/", params=params, headers=headers, data=body)
                if "verify_center_decision_conf" in r:
                    data = json.loads(r)["data"]
                    captcha = json.loads(data["verify_center_decision_conf"])
                    self.solve_captcha(detail=captcha["detail"], type=captcha["type"], subtype=captcha["subtype"])
                else:
                    break
            print(r)

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
        body = json.dumps({
            "codeChannel": 1,
            "target": number,
            "country": country_code,
            "isCipher": False
        })
        params = {
                "lang": self.language,
                "language": self.language
            }
        for _ in range(2):
            r = self._xhr("POST", "https://www.tiktok.com/api/ba/business/suite/verification/contact/send/", params=params, headers=headers, data=body)
            if "codeDecisionConf" in r:
                data = json.loads(r)
                captcha = json.loads(data["codeDecisionConf"])
                self.solve_captcha(detail=captcha["detail"], type=captcha["type"], subtype=captcha["subtype"])
            else:
                break
        print(r)

    def solve_captcha(self, detail: str, type: str, subtype: str):
        params = {
            "lang": self.language,
            "app_name": "",
            "h5_sdk_version": "2.26.18",
            "sdk_version": "3.5.0-alpha.1",
            "iid": "0",
            "did": "0",
            "device_id": "0",
            "ch": "web_text",
            "aid": "1988",
            "os_type": "2",
            "mode": "",
            "tmp": "1701289845878",
            "platform": self.platform,
            "webdriver": "false",
            "fp": self.verify_fp,
            "type": type,
            "detail": detail,
            "server_sdk_env": "%7B%22idc%22:%22useast5%22,%22region%22:%22US-TTP%22,%22server_type%22:%22business%22%7D",
            "subtype": subtype,
            "challenge_code": "3058",
            "os_name": "windows",
            "h5_check_version": "3.5.0-alpha.1"
        }
        r = self._xhr("GET", "https://verification.us.tiktok.com/captcha/get", params=params)
        data = json.loads(r)["data"]
        id = data["id"]
        challenge_code = str(data["challenge_code"])
        mode = data["mode"]

        if subtype == "3d":
            omocaptcha = OMOCaptcha("vBGRE4v2HuzbHytf9NZ6fHkuZirmcxmJXP00HkK9HUUVaf6LQmRNdeXJ9u0Pt8PqG9o24kIQ4Ecopnix")
            image_url = data["question"]["url1"]
            x1, y1, x2, y2 = omocaptcha.solve_tiktok_2objects(image_url=image_url)
            answer = [
                {
                    "x": x1,
                    "y": y1
                },
                {
                    "x": x2,
                    "y": y2
                }
            ]
        elif subtype == "whirl":
            omocaptcha = OMOCaptcha("vBGRE4v2HuzbHytf9NZ6fHkuZirmcxmJXP00HkK9HUUVaf6LQmRNdeXJ9u0Pt8PqG9o24kIQ4Ecopnix")
            outer_image_url = data["question"]["url1"]
            inner_image_url = data["question"]["url2"]
            x = omocaptcha.solve_tiktok_rotation(outer_image_url=outer_image_url, inner_image_url=inner_image_url)
            answer = [{"x": i, "y": 0, "relative_time": i + 50} for i in range(x+1)]

        headers = {
            "Content-Type": "application/json"
        }
        body = json.dumps({
            "modified_img_width": 340,
            "id": id,
            "mode": mode,
            "reply": answer,
            "reply2": answer,
            "drag_width": 271
        })
        params["mode"] = mode
        params["challenge_code"] = challenge_code
        r = self._xhr("POST", "https://verification.us.tiktok.com/captcha/verify", params=params, headers=headers, data=body)
        print(r)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.browser.close()
        self.playwright.stop()
