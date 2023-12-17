from tiktok_py import TikTok

with open("sessions.txt") as f:
    sessions = f.read().splitlines()

if __name__ == "__main__":
    for session in sessions:
        with TikTok(headless=True, omocaptcha_api_key="vBGRE4v2HuzbHytf9NZ6fHkuZirmcxmJXP00HkK9HUUVaf6LQmRNdeXJ9u0Pt8PqG9o24kIQ4Ecopnix") as bot:
            try:
                bot.login(session=session)
                bot.comment("https://www.tiktok.com/@user27435856296163/video/7313298568352206112", "nice")
            except Exception as e:
                print(e)
            finally:
                # input("Press enter to continue...")
                pass
