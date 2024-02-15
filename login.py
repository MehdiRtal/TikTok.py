from tiktok_py import TikTok
from icecream import ic
import os


with open(os.path.join(os.path.dirname(__file__), "accounts.txt")) as f:
    accounts = f.read().splitlines()

for account in accounts:
    try:
        with TikTok(
            proxy="11613371-all-country-DE-state-2905330-city-2925533-session-3:242kh3l5bl@93.190.138.107:14740",
            omocaptcha_api_key="MNTsnIAWFsenRoDYWFSxclP2uqxEyc3Ifn1FW1XNTTyzotSLC9TWH1ZzVByGfa8zETRuzSaBptiY9QYJ",
            headless=False
        ) as tt:
            tt.login(username=account.split(":")[0], password=account.split(":")[1])
    except Exception as e:
        ic(e)
    else:
        print("Success")
        with open(os.path.join(os.path.dirname(__file__), "sessions.txt"), "a+") as f:
            f.write(tt.session + "\n")
