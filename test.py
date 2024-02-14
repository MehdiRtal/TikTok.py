from tiktok_py import TikTok
from icecream import ic
import os


with open(os.path.join(os.path.dirname(__file__), "sessions.txt")) as f:
    sessions = f.read().splitlines()

for session in sessions:
    try:
        with TikTok(omocaptcha_api_key="MNTsnIAWFsenRoDYWFSxclP2uqxEyc3Ifn1FW1XNTTyzotSLC9TWH1ZzVByGfa8zETRuzSaBptiY9QYJ") as tt:
            tt.login(session=session)
            #tt.follow("alos314")
            tt.like("https://www.tiktok.com/@alos314/video/7257653393747987718")
    except Exception as e:
        ic(e)
    else:
        print("Success")
