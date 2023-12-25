from tiktok_py import TikTok
import base64
import httpx
import random

with open("sessions.txt") as f:
    sessions = f.read().splitlines()

with open("avatars.txt") as f:
    avatars = f.read().splitlines()

if __name__ == "__main__":
    for session in sessions:
        with TikTok(headless=True, omocaptcha_api_key="vBGRE4v2HuzbHytf9NZ6fHkuZirmcxmJXP00HkK9HUUVaf6LQmRNdeXJ9u0Pt8PqG9o24kIQ4Ecopnix") as bot:
            try:
                bot.login(session=session)

                bot.like("https://www.tiktok.com/@yasnime21/photo/7314030475981638918")

                # bot.follow("yasnime21")

                # url = random.choice(avatars)
                # avatar = httpx.get(url).content
                # avatar_b64 = base64.b64encode(avatar).decode("utf-8")
                # bot.edit_profile(avatar=avatar_b64)
            except Exception as e:
                print(e)
            finally:
                # input("Press enter to continue...")
                pass
