from tiktok_py import TikTok
import traceback
import os


with open(os.path.join(os.path.dirname(__file__), "accounts.txt")) as f:
    accounts = f.read().splitlines()

for account in accounts:
    with TikTok(
        proxy="",
        omocaptcha_api_key="MNTsnIAWFsenRoDYWFSxclP2uqxEyc3Ifn1FW1XNTTyzotSLC9TWH1ZzVByGfa8zETRuzSaBptiY9QYJ",
        headless=True
    ) as tt:
        try:
            tt.login(username=account.split(":")[0], password=account.split(":")[1])
        except Exception:
            traceback.print_exc()
        else:
            print("Success")
            with open(os.path.join(os.path.dirname(__file__), "sessions.txt"), "a+") as f:
                f.write(tt.session + "\n")
        # finally:
        #     input()
