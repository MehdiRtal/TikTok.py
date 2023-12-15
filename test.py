from tiktok_py import TikTok
import json

with open("sessions.txt") as f:
    sessions = f.read().splitlines()

if __name__ == "__main__":
    for session in sessions:
        try:
            session = json.loads(session)
            with TikTok(headless=False, omocaptcha_api_key="vBGRE4v2HuzbHytf9NZ6fHkuZirmcxmJXP00HkK9HUUVaf6LQmRNdeXJ9u0Pt8PqG9o24kIQ4Ecopnix") as bot:
                bot.login(session=session)
                bot.like("https://www.tiktok.com/@hissy.0/video/7311313600663112993")
        except Exception as e:
            print(e)
