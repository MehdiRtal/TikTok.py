from tiktok_py import TikTok
from icecream import ic
import os


with open(os.path.join(os.path.dirname(__file__), "accounts.txt")) as f:
    accounts = f.read().splitlines()

for account in accounts:
    try:
        with TikTok(omocaptcha_api_key="MNTsnIAWFsenRoDYWFSxclP2uqxEyc3Ifn1FW1XNTTyzotSLC9TWH1ZzVByGfa8zETRuzSaBptiY9QYJ") as tt:
            tt.login(username=account.split(":")[0], password=account.split(":")[1])
    except Exception as e:
        ic(e)
    else:
        print("Success")
        with open(os.path.join(os.path.dirname(__file__), "sessions.txt"), "a+") as f:
            f.write(tt.session + "\n")
