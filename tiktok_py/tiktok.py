from playwright.sync_api import sync_playwright
import json
from fake_useragent import UserAgent
import random
from omocaptcha_py import OMOCaptcha
from requests.models import PreparedRequest
from playwright_stealth import stealth_sync, StealthConfig

from tiktok_py.utils import encrypt_login, generate_verify, extract_aweme_id


class TikTok:
    def __init__(self, headless: bool = False, proxy: str = None, omocaptcha_api_key: str = None, user_agent: str = None):
        self.omocaptcha_api_key = omocaptcha_api_key
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
        self.browser = self.playwright.firefox.launch(headless=headless, proxy=tmp_proxy)
        if user_agent:
            self.user_agent = user_agent
        else:
            ua = UserAgent(browsers=["firefox"], os=["windows"])
            self.user_agent = ua.random
            # self.user_agent = None
        self.context = self.browser.new_context(user_agent=self.user_agent)
        self.context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["stylesheet", "font", "manifest", "other"] else route.continue_())
        self.page = self.context.new_page()
        stealth_sync(
            self.page,
            StealthConfig(
                webdriver=True,
                webgl_vendor=True,
                chrome_app=False,
                chrome_csi=False,
                chrome_load_times=False,
                chrome_runtime=False,
                iframe_content_window=True,
                media_codecs=True,
                navigator_hardware_concurrency=4,
                navigator_languages=False,
                navigator_permissions=True,
                navigator_platform=False,
                navigator_plugins=True,
                navigator_user_agent=False,
                navigator_vendor=False,
                outerdimensions=True,
                hairline=False,
            )
        )
        self.language = self.page.evaluate("() => navigator.language || navigator.userLanguage")
        self.platform = self.page.evaluate("() => navigator.platform")
        self.browser_version = self.page.evaluate("() => navigator.appVersion")
        self.history_len = str(random.randint(1, 10))
        self.screen_height = str(random.randint(600, 1080))
        self.screen_width = str(random.randint(800, 1920))
        self.timezone = self.page.evaluate("() => Intl.DateTimeFormat().resolvedOptions().timeZone")
        self.verify_fp = ""
        self.device_id = ""
        self.csrf_token = ""
        self.session = None

    def _xhr(self, method: str, url: str, params: dict = None, headers: dict = "", data: str = None):
        if params:
            req = PreparedRequest()
            req.prepare_url(url, params)
            url = req.url
        if headers:
            headers = "n".join([f"xhr.setRequestHeader('{k}', '{v}');" for k, v in headers.items()])
        expression = f"""
            (o) => {{
                return new Promise((resolve, reject) => {{
                    let xhr = new XMLHttpRequest();
                    xhr.open(o.method, o.url);
                    {headers}
                    xhr.onload = () => resolve(xhr.responseText);
                    xhr.onerror = () => reject(xhr.statusText);
                    xhr.send(o.data);
                }});
            }}
        """
        r = self.page.evaluate(expression, {"url": url, "method": method, "data": data})
        return r

    def _fetch(self, method: str, url: str, params: dict = None, headers: dict = {}, data: str = None) -> str:
        if params:
            params.update({
                "WebIdLastTime": "",
                "aid": "1988",
                "app_language": self.language,
                "app_name": "tiktok_web",
                "browser_language": self.language,
                "browser_name": "Mozilla",
                "browser_online": "true",
                "browser_platform": self.platform,
                "browser_version": self.browser_version,
                "channel": "tiktok_web",
                "cookie_enabled": "true",
                "device_id": self.device_id,
                "device_platform": "web_pc",
                "focus_state": "true",
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
                "verifyFp": self.verify_fp,
                "webcast_language": self.language
            })
            req = PreparedRequest()
            req.prepare_url(url, params)
            url = req.url
        expression = """
            async (o) => {
                if (typeof o.data === 'object' && o.data !== null && 'avatar' in o.data) {
                    formData = new FormData();
                    const byteString = atob(o.data.avatar);
                    const byteArray = new Uint8Array(byteString.length);
                    for (let i = 0; i < byteString.length; i++) {
                        byteArray[i] = byteString.charCodeAt(i);
                    }
                    blob = new Blob([byteArray], { type: 'image/jpeg' });
                    formData.append('file', blob);
                    formData.append('source', 0)
                    requestBody = formData;
                } else {
                    requestBody = o.data;
                }
                response = await fetch(o.url, { method: o.method, headers: o.headers, body: requestBody });
                return response.text();
            }
        """
        r = self.page.evaluate(expression, {"url": url, "method": method, "headers": headers, "data": data})
        return r

    def login(self, username: str = None, password: str = None, session: dict = None):
        self.page.goto("https://www.tiktok.com/login/phone-or-email/email", wait_until="networkidle")
        data = json.loads(self.page.locator("id=__UNIVERSAL_DATA_FOR_REHYDRATION__").inner_text())
        self.device_id = data["__DEFAULT_SCOPE__"]["webapp.app-context"]["wid"]
        if session:
            self.session = json.loads(session)
            self.context.add_cookies(self.session)
            self.verify_fp = next((cookies["value"] for cookies in self.context.cookies() if cookies["name"] == "s_v_web_id"), "")
        elif username and password:
            self.verify_fp = generate_verify()
            self.context.add_cookies([{"name": "s_v_web_id", "value": self.verify_fp, "domain": ".tiktok.com", "path": "/"}])
            username = encrypt_login(username)
            password = encrypt_login(password)
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            body = f"mix_mode=1&username={username}&email={username}&password={password}&aid=1459&is_sso=false&account_sdk_source=web&region=MA&language={self.language}&did={self.device_id}&fixed_mix_mode=1"
            params = {
                "multi_login": "1",
                "did": self.device_id,
                "aid": "1459",
                "account_sdk_source": "web",
                "sdk_version": "2.0.3-tiktok",
                "language": self.language,
                "verifyFp": self.verify_fp,
                "target_aid": "",
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
                    "browser_version": self.browser_version,
                    "browser_online": True,
                    "verifyFp": self.verify_fp,
                    "app_language": self.language,
                    "webcast_language": self.language,
                    "tz_name": self.timezone,
                    "is_page_visible": True,
                    "focus_state": True,
                    "is_fullscreen": False,
                    "history_len": self.history_len
                }, separators=(",", ":")),
                "fp": self.verify_fp
            }
            r = self._xhr("POST", "https://www.tiktok.com/passport/web/user/login/", params=params, headers=headers, data=body)
            r_json = json.loads(r)
            if "verify_center_decision_conf" in r_json["data"]:
                captcha = json.loads(r_json["data"]["verify_center_decision_conf"])
                self.solve_captcha(detail=captcha["detail"], type=captcha["type"], subtype=captcha["subtype"], region=captcha["region"])
                r = self._xhr("POST", "https://www.tiktok.com/passport/web/user/login/", params=params, headers=headers, data=body)
                r_json = json.loads(r)
            if r_json["message"] != "success":
                raise Exception("Login failed")
            self.session = json.dumps(self.context.cookies())
        self.csrf_token = next((cookies["value"] for cookies in self.context.cookies() if cookies["name"] == "tt_csrf_token"), "")

    def get_user_info(self, username: str):
        params = {
            "from_page": "fyp",
            "secUid": "",
            "uniqueId": username
        }
        r = self._fetch("GET", "https://www.tiktok.com/api/user/detail/", params=params)
        r_json = json.loads(r)
        if r_json["status_code"] != 0:
            raise Exception("Get user info failed")
        return r_json

    def edit_profile(self, nickname: str = None, bio: str = None, avatar: str = None):
        body = []
        if bio:
            body.append(f"signature={bio}")
        if nickname:
            body.append(f"nickname={nickname}")
        if avatar:
            _body = {"avatar": avatar}
            params = {
                "from_page": "user"
            }
            r = self._fetch("POST", "https://www.tiktok.com/api/upload/image/", params=params, data=_body)
            r_json = json.loads(r)
            if r_json["status_code"] != 0:
                raise Exception("Upload avatar failed")
            avatar_uri = r_json["data"]["uri"]
            body.append(f"avatar_uri={avatar_uri}")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        body = "&".join(body)
        params = {
            "from_page": "user"
        }
        r = self._fetch("POST", "https://www.tiktok.com/api/update/profile/", params=params, headers=headers, data=body)
        r_json = json.loads(r)
        if r_json["status_code"] != 0:
            raise Exception("Edit profile failed")

    def comment(self, url: str, text: str):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Tt-Csrf-Token": self.csrf_token
        }
        body = ""
        params = {
            "aweme_id": extract_aweme_id(url),
            "from_page": "video",
            "text": text,
            "text_extra": "[]"
        }
        r = self._fetch("POST", "https://www.tiktok.com/api/comment/publish/", params=params, headers=headers, data=body)
        r_json = json.loads(r)
        if r_json["status_code"] != 0:
            raise Exception("Comment failed")

    def like(self, url: str):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Tt-Csrf-Token": self.csrf_token
        }
        body = ""
        params = {
            "aweme_id": extract_aweme_id(url),
            "from_page": "fyp",
            "type": "1"
        }
        r = self._fetch("POST", "https://www.tiktok.com/api/commit/item/digg/", params=params, headers=headers, data=body)
        r_json = json.loads(r)
        if r_json["status_code"] != 0 or r_json["is_digg"] == 1:
            raise Exception("Like failed")

    def follow(self, username: str):
        user = self.get_user_info(username)["user"]
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Tt-Csrf-Token": self.csrf_token
        }
        body = ""
        params = {
            "action_type": "1",
            "from": "18",
            "fromWeb": "1",
            "from_page": "fyp",
            "from_pre": "0",
            "sec_user_id": user["secUid"],
            "type": "1",
            "user_id": user["id"]
        }
        r = self._fetch("POST", "https://www.tiktok.com/api/commit/follow/user/", params=params, headers=headers, data=body)
        r_json = json.loads(r)
        if r_json["status_code"] != 0:
            raise Exception("Follow failed")

    def save(self, url: str):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Tt-Csrf-Token": self.csrf_token
        }
        body = ""
        params = {
            "action": "1",
            "from_page": "fyp",
            "itemId": extract_aweme_id(url),
            "secUid": ""
        }
        r = self._fetch("POST", "https://www.tiktok.com/api/item/collect/", params=params, headers=headers, data=body)
        r_json = json.loads(r)
        if r_json["status_code"] != 0:
            raise Exception("Save failed")

    def contact(self, number: str, country_code: str, sms: bool = False):
        headers = {
            "Content-Type": "application/json"
        }
        body = json.dumps({
            "userData": json.dumps({
                "session_id": "f24220cdf06b0818d42b784a1",
                "isDraft": True,
                "formData": {
                    "companyBasicInfo": {
                        "addressDetail": "",
                        "area": "",
                        "businessVerificationId": "",
                        "city": "",
                        "companyName": "",
                        "country": "",
                        "dnbCode": "",
                        "number": "",
                        "phone": "",
                        "postalCode": "",
                        "state": "",
                        "website": ""
                    },
                    "dnbData": None,
                    "dnbId": "",
                    "qualificationUrls": [],
                    "source": None
                },
                "policyConfirmed": True,
                "currentStep": "basicInformation"
            })
        })
        params = {
                "lang": self.language,
                "language": self.language
        }
        r = self._xhr("POST", "https://www.tiktok.com/api/ba/business/suite/verification/draft/update/", params=params, headers=headers, data=body)
        r_json = json.loads(r)
        if r_json["status_code"] != 0:
            raise Exception("Verify business failed")

        headers = {
            "Content-Type": "application/json"
        }
        body = json.dumps({
            "companyBasicInfo": {
                "addressDetail": "SDSDFSDGDFG",
                "businessVerificationId": "5456453453486",
                "city": "Arapiraca",
                "companyName": "FSDF",
                "country": "BR",
                "dnbCode": "",
                "phone": "+244SDGDFGHFGHSDF",
                "postalCode": "FGSFSDF",
                "state": "Alagoas",
                "website": ""
            },
            "userData": json.dumps({
                "session_id": "f24220cdf06b0818d42b784a1",
                "isDraft": True,
                "formData": {
                    "companyBasicInfo": {
                        "addressDetail": "SDSDFSDGDFG",
                        "area": "+244",
                        "businessVerificationId": "5456453453486",
                        "city": "Arapiraca",
                        "companyName": "FSDF",
                        "country": "BR",
                        "dnbCode": "",
                        "number": "SDGDFGHFGHSDF",
                        "phone": "+244SDGDFGHFGHSDF",
                        "postalCode": "FGSFSDF",
                        "state": "Alagoas",
                        "website": ""
                    },
                    "dnbData": None,
                    "dnbId": "",
                    "qualificationUrls": [],
                    "source": None
                },
                "policyConfirmed": True,
                "currentStep": "basicInformation",
                "hasDraft": True
            })
        })
        params = {
                "lang": self.language,
                "language": self.language
        }
        r = self._xhr("POST", "https://www.tiktok.com/api/ba/business/suite/verification/company/list/", params=params, headers=headers, data=body)
        r_json = json.loads(r)
        if r_json["statusCode"] != 0:
            raise Exception("Basic info failed")

        headers = {
            "Content-Type": "application/json"
        }
        body = json.dumps({
            "userData": json.dumps({
                "session_id": "f24220cdf06b0818d42b784a1",
                "isDraft": True,
                "formData": {
                    "companyBasicInfo": {
                        "addressDetail": "SDSDFSDGDFG",
                        "area": "+244",
                        "businessVerificationId": "5456453453486",
                        "city": "Arapiraca",
                        "companyName": "FSDF",
                        "country": "BR",
                        "dnbCode": "",
                        "number": "SDGDFGHFGHSDF",
                        "phone": "+244SDGDFGHFGHSDF",
                        "postalCode": "FGSFSDF",
                        "state": "Alagoas",
                        "website": ""
                    },
                    "dnbData": None,
                    "dnbId": "",
                    "qualificationUrls": ["/wsos_v2/certification_center/object/wsos65b2cf13488f4b08?timeStamp=1706221634&sign=58fb40b4d7219be9de60a15388438709a056301947f5489094edfa82e7cbb179"],
                    "source": 1
                },
                "policyConfirmed": True,
                "currentStep": "verifyAccess"
            })
        })
        params = {
                "lang": self.language,
                "language": self.language
        }
        r = self._xhr("POST", "https://www.tiktok.com/api/ba/business/suite/verification/draft/update/", params=params, headers=headers, data=body)
        r_json = json.loads(r)
        if r_json["status_code"] != 0:
            raise Exception("Verify business failed")

        headers = {
            "Content-Type": "application/json"
        }
        body = json.dumps({
            "codeChannel": 2 if sms else 1,
            "target": number,
            "country": country_code,
            "isCipher": False
        })
        params = {
                "lang": self.language,
                "language": self.language
            }
        r = self._xhr("POST", "https://www.tiktok.com/api/ba/business/suite/verification/contact/send/", params=params, headers=headers, data=body)
        r_json = json.loads(r)
        if "codeDecisionConf" in r_json:
            captcha = json.loads(r_json["codeDecisionConf"])
            self.solve_captcha(detail=captcha["detail"], type=captcha["type"], subtype=captcha["subtype"], region=captcha["region"])
            r = self._xhr("POST", "https://www.tiktok.com/api/ba/business/suite/verification/contact/send/", params=params, headers=headers, data=body)
            r_json = json.loads(r)
        if r_json["status_code"] != 0:
            raise Exception("Call failed")

    def solve_captcha(self, detail: str, type: str, subtype: str, region: str):
        if region == "ie":
            url = "https://rc-verification.tiktokv.eu"
        elif region == "in":
            url = "https://rc-verification-i18n.tiktokv.com"
        elif region == "sg":
            url = "https://rc-verification-sg.tiktokv.com"
        elif region == "ttp":
            url = "https://rc-verification16-normal-useast5.tiktokv.us"
        elif region == "ttp2":
            url = "https://rc-verification16-normal-useast8.tiktokv.us"
        elif region == "va":
            url = "https://rc-verification-va.tiktokv.com"

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
            "tmp": "1702250765984",
            "platform": self.platform,
            "webdriver": "false",
            "fp": self.verify_fp,
            "type": type,
            "detail": detail,
            "server_sdk_env": "%7B%22idc%22:%22sg1%22,%22region%22:%22ALISG%22,%22server_type%22:%22business%22%7D",
            "subtype": subtype,
            "challenge_code": "3058",
            "os_name": "windows",
            "h5_check_version": "3.5.0-alpha.1"
        }
        r = self._xhr("GET", f"{url}/captcha/get", params=params)
        r_json = json.loads(r)
        if r_json["code"] != 200:
            raise Exception("Get captcha failed")
        data = r_json["data"]
        id = data["id"]
        challenge_code = str(data["challenge_code"])
        mode = data["mode"]

        omocaptcha = OMOCaptcha(self.omocaptcha_api_key)
        body = {}
        if subtype == "3d":
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
            outer_image_url = data["question"]["url1"]
            inner_image_url = data["question"]["url2"]
            x = omocaptcha.solve_tiktok_rotation(outer_image_url=outer_image_url, inner_image_url=inner_image_url)
            answer = [{"x": i, "y": 0, "relative_time": i + 50} for i in range(x+1)]
            body["drag_width"] = 271

        headers = {
            "Content-Type": "application/json"
        }
        body.update({
            "modified_img_width": 340,
            "id": id,
            "mode": mode,
            "reply": answer,
            "reply2": answer,
        })
        body = json.dumps(body)
        params["mode"] = mode
        params["challenge_code"] = challenge_code
        r = self._xhr("POST", f"{url}/captcha/verify", params=params, headers=headers, data=body)
        r_json = json.loads(r)
        if r_json["code"] != 200:
            raise Exception("Solve captcha failed")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.browser.close()
        self.playwright.stop()
