from tiktok_py import TikTok
import traceback
import os


with open(os.path.join(os.path.dirname(__file__), "sessions.txt")) as f:
    sessions = f.read().splitlines()

for session in sessions:
    with TikTok(
        omocaptcha_api_key="MNTsnIAWFsenRoDYWFSxclP2uqxEyc3Ifn1FW1XNTTyzotSLC9TWH1ZzVByGfa8zETRuzSaBptiY9QYJ",
        headless=False
    ) as tt:
        try:
            tt.login(session=session)
            #tt.follow("alos314")
            tt.like("https://www.tiktok.com/@alos314/video/7257653393747987718")
        except Exception:
            traceback.print_exc()
        else:
            print("Success")
        # finally:
        #     input()
