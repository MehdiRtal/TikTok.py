from playwright.sync_api import sync_playwright
import urllib.parse
import json
from fake_useragent import UserAgent
import random
from playwright_stealth import stealth_sync
from omocaptcha import OMOCaptcha


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
        self.verify_fp = "verify_lp8tr78m_QbiwfvPC_boiZ_4TvS_9jak_6cc3vDkimkxz"

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

    def login(self, session: dict = None):
        if session:
            self.page.context.add_cookies(session)
        self.page.goto("https://www.tiktok.com/")

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
        while True:
            r = self._xhr("POST", "https://www.tiktok.com/api/ba/business/suite/verification/contact/send/?lang=ar&language=ar", headers=headers, data=data)
            if "codeDecisionConf" in r:
                captcha = json.loads(json.loads(r)["codeDecisionConf"])
                self.solve_captcha(detail=captcha["detail"], type=captcha["type"], subtype=captcha["subtype"])
            else:
                break
        print(r)

    def solve_captcha(self, detail: str, type: str, subtype: str):
        detail = "36mMOyT2xRjCrvYMG-YU4Hrqg*q7nhQlChaZkRvGLB9cUC2YwY-QVnY07YvNTWHHRVVI0zadHGJT1MGpQa-zS4DQPQ5CKIIICnlwhdpjyncQRuNaKd862g*F-QjZ4hVmQIZ6yN*b-JYrKmFe1gn*1h8C1x0Ex0C7-TT8XdvgK7yWU3GoQ76KdCqf-BZdCrKDhRvWuZGOVaikxrFN0nhBWyJO4V*FV20ukYwNtanvMuB3FsriN5N8B9NDC29bfHs."
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
            "tmp": "1701254862883",
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
        image_url = data["question"]["url1"]

        if subtype == "3d":
            omocaptcha = OMOCaptcha("vBGRE4v2HuzbHytf9NZ6fHkuZirmcxmJXP00HkK9HUUVaf6LQmRNdeXJ9u0Pt8PqG9o24kIQ4Ecopnix")
            x1, y1, x2, y2 = omocaptcha.solve_tiktok_2objects(image_url=image_url, width=340, height=212)

        headers = {
            "Content-Type": "application/json"
        }
        body = {
            "modified_img_width": 340,
            "id": id,
            "mode": mode,
            "reply": [
                {
                    "x": x1,
                    "y": y1
                },
                {
                    "x": x2,
                    "y": y2
                }
            ],
            "reply2": [
                {
                    "x": x1,
                    "y": y1
                },
                {
                    "x": x2,
                    "y": y2
                }
            ],
        }
        params["mode"] = mode
        params["challenge_code"] = challenge_code
        r = self._xhr("POST", "https://verification.us.tiktok.com/captcha/verify", params=params, headers=headers, data=json.dumps(body))
        print(r)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.browser.close()
        self.playwright.stop()


if __name__ == "__main__":
    with TikTok(headless=False) as bot:
        c = "tt-target-idc-sign=gPMhzDWqHwTsUwKVRu254ElcU0gtMhhuKTn6be8CP8OlRbAhs4pvTOcB40Brzxl9eg8K6ycIeS4UA0u3lLusfx4BMvX2Gs-F-ggDUm-2ld_6Cl3euzl3WSpyU0ilX1B5csdxuOd-xxZTwQgpanoJsUL--hV8m93csz31a9uDSCtnIi-8Pt9ENl74ty9Zpnf0TVCT1d_mt7owtEST0cT0AdetHAiqZj-UbWo1HXOmv0KJNCWoaJvKF2zg-PqNrgxE0xqh1rzU_Pjo9c5cgKzi-Pn20xPuoq3jefwoYboLb0NP9ftsHijRs6qoy6GmLIY3TfxOBMlPjKyKMKP9q4hKrgGmQcA-8MaW04eLHzZMyNs-3wpgDvCta69kkdS5HtFcMRh8bD2fhuVfQuoJYTxuJzHuj81BY0DQTgpLb8-X_lBHS0DKw0p5lWbbm18_c9Ksu2pcU9xUwpx3kR_vnfWGLmPG54FhRhJ9h55xtoY15tGzDVTx_O4u81MHWGJTCI1x;csrf_session_id=b21434d1aed8bd3db7b949c64aec0cba;msToken=3VnQc1UvxlL7pahD9omQr-Fnb9JvWa_fmsGbIQ4BuEQVMLfNFCBKU4JMnvPa9OMCnEDAL9wiYGbWcYnfDuyQCljBlJLn3EkGoNDqTF6MTqVSiJJ8yC5HHWeLEgdJ301cD6Vu6FM6xu-GC0Y=;gd_random_756329=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDE3MDYyNzYsImlhdCI6MTcwMTEwMTQ3NiwibWF0Y2giOmZhbHNlLCJuYmYiOjE3MDExMDE0NzYsInBhdGgiOiIvYnVzaW5lc3Mtc3VpdGUiLCJwZXJjZW50IjowLjEyNTk2NTU5Nzc3MjMzNzl9.e8t119XWMht0RAR42dXOVb58AEQLKHiuig88u8pqSjk;sid_guard=78034e564d3a73c506ee3ff11f37166a%7C1701252902%7C15552000%7CMon%2C+27-May-2024+10%3A15%3A02+GMT;ttwid=1%7CXDb88SaCLj_N4zF_qpbCcB5l6idnfrHr4M36B3ZFOnI%7C1701252597%7Cac5709d05a4bd536c1fd4584516303e22f2846c184c8c748baa9ae811be64ffe;store-country-code-src=uid;perf_feed_cache={%22expireTimestamp%22:1701424800000%2C%22itemIds%22:[%227299161189072882962%22%2C%227294698096750038278%22%2C%227282872981179665682%22]};cookie-consent={%22ga%22:true%2C%22af%22:true%2C%22fbp%22:true%2C%22lip%22:true%2C%22bing%22:true%2C%22ttads%22:true%2C%22reddit%22:true%2C%22hubspot%22:true%2C%22version%22:%22v10%22};uid_tt=be4722bd49666483abe02fd3fedb96e7a3471708ec0db18529883efbc92bc11a;passport_csrf_token_default=e57ebea098d4ad5a28d15da3b8638a73;msToken=tES4FkOz3kBz597T4QnRNsEz935L02fS0GnXgwIFqxXUylMPWpH2n8YqiT8owNqKn6zRH5d0R6UxLZ_9rAT10CO53h_rmXBYQU1Trq9hwCUT-0F-hMNMgoOFPEFuaDxbT4t11t0Gnuw1Uq0=;s_v_web_id=verify_lp8tr78m_QbiwfvPC_boiZ_4TvS_9jak_6cc3vDkimkxz;store-idc=useast5;ssid_ucp_v1=1.0.0-KDc1N2UzZDIzYWM1MTViY2YxN2Y4NDVlNmM1MjY3NTYzNTIxMTAxYzIKIAiuiPuK1p2CjWUQpp6cqwYYswsgDDDYkuioBjgBQOoHEAQaB3VzZWFzdDUiIDc4MDM0ZTU2NGQzYTczYzUwNmVlM2ZmMTFmMzcxNjZh;tiktok_webapp_theme=light;__tea_cache_tokens_1988={%22user_unique_id%22:%227304024311227008545%22%2C%22timestamp%22:1701252748171%2C%22_type_%22:%22default%22};_ttp=2XoQKxlaBhIiD1WViyCsg3h5Kwv;cmpl_token=AgQQAPNSF-RO0rUk5krpbB0X_zyCWgof_6O3YNM-Uw;csrfToken=ScRlNFZR-sbfBVAtblEORoKtKmv9HvSlJBQI;gd_random_756330=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDE3MDMwMjEsImlhdCI6MTcwMTA5ODIyMSwibWF0Y2giOmZhbHNlLCJuYmYiOjE3MDEwOTgyMjEsInBhdGgiOiIvYnVzaW5lc3Mtc3VpdGUiLCJwZXJjZW50IjowLjY3ODcyMjU4ODY3MjQzMzV9.OTQ0opjHefARgywM9VbmhHYqNlHDOPZU-2GaKLarJsw;gd_worker_v2_random_3285=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDE4NTc3MDksImlhdCI6MTcwMTI1MjkwOSwibWF0Y2giOmZhbHNlLCJuYmYiOjE3MDEyNTI5MDksInBhdGgiOiIvYnVzaW5lc3Mtc3VpdGUiLCJwZXJjZW50IjowLjU1NzYxMTM5NDM2OTg1NTd9.gA6WbLr8LJRoRDfWLQ1gxF3igv_Cl9y5f0f3XHSTIgA;multi_sids=7285145162859070510%3A78034e564d3a73c506ee3ff11f37166a;odin_tt=e255ed99c87411f8dde0dbd5763b1be07a30cb6eb87441c6c28b4f850b1969d5c5b3e403eb7083d1a21d46929cab014c90dcb4f22b12be3e29c8a7012895867b;passport_csrf_token=e57ebea098d4ad5a28d15da3b8638a73;passport_fe_beating_status=false;sessionid=78034e564d3a73c506ee3ff11f37166a;sessionid_ss=78034e564d3a73c506ee3ff11f37166a;sid_tt=78034e564d3a73c506ee3ff11f37166a;sid_ucp_v1=1.0.0-KDc1N2UzZDIzYWM1MTViY2YxN2Y4NDVlNmM1MjY3NTYzNTIxMTAxYzIKIAiuiPuK1p2CjWUQpp6cqwYYswsgDDDYkuioBjgBQOoHEAQaB3VzZWFzdDUiIDc4MDM0ZTU2NGQzYTczYzUwNmVlM2ZmMTFmMzcxNjZh;store-country-code=us;tt-target-idc=useast5;tt_chain_token=6lI25awe8YMJR/5WfdRb0g==;tt_csrf_token=7qq6kCPG-joZNz748aSlXRo7hx4xjH8Z6Tpg;uid_tt_ss=be4722bd49666483abe02fd3fedb96e7a3471708ec0db18529883efbc92bc11a"
        c = [{"name": i.split("=")[0], "value": i.split("=")[1], "domain": ".tiktok.com", "path": "/"} for i in c.split(";") if i]
        bot.login(session=c)
        bot.call(number="+212691617955", country_code="BR")
        # bot.solve_captcha(type="verify", subtype="3d", detail="LmIb9z1LPSFKjAffksnj8iWsfkgzPQob6pCZEmyTg26-UZCeSs8m1C0OKX02Ye*huzZqNd1WHWl9gLoot7MrsZ14gZ1vESL4aCQVPkbt*keuKGLA6af9r7p0L3Xw7OESuj2aN*aPTduHamJYIW6P1Qg9YOCgHJGJyi87NJb3eurzFUccIcRgw9pGLLEHCO-3fK5FOWiLsVDfKpsq0L8Lw32XAP3pwoZcW1IaDjw72VKx7MnZ10Bfu*FWMCwEn2MkAFz*OpHv-qqdOvpkVqagcOiYa2Nn6fdekiJ5jiq2EPebxMvXsOCXAzxeW*tL-Vuk48BMqBDxWitQulninzV*oCrMPVT6YaFTxJ9Y*8wkvg7ULkmgiLWXhKNujmrB3n50wy5vfqMhgC1MwNG0dNyxvff4OEvGtl1lgRilHcLIyCmq8VIfT11ARAexOK7TgypQt10zKikTM5-wH0cylZ-d8rPKlhzveiMScKGfOjZ69es7-69ISQ..")
