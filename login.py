from tiktok_py import TikTok

with open("accounts.txt", "r") as f:
    accounts = f.read().splitlines()

if __name__ == "__main__":
    for account in accounts:
        with TikTok(headless=False, omocaptcha_api_key="vBGRE4v2HuzbHytf9NZ6fHkuZirmcxmJXP00HkK9HUUVaf6LQmRNdeXJ9u0Pt8PqG9o24kIQ4Ecopnix") as bot:
            try:
                bot.login(username=account.split(":")[0], password=account.split(":")[1])
            except Exception as e:
                print(e)
                input("Press Enter to continue...")
            else:
                print("Success")
                with open("sessions.txt", "a+") as f:
                    f.write(bot.session + "\n")
