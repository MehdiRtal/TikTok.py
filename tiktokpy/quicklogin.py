import asyncio

from tiktokpy import TikTokPy


async def main():
    async with TikTokPy() as bot:
        await bot.login_session()

asyncio.run(main())
