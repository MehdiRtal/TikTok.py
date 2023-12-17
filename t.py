from TikTokAPI.tiktok_browser import TikTokBrowser

browser = TikTokBrowser(user_agent="Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36")

print(browser.fetch_auth_params(""))
