import asyncio

from tiktokpy import TikTokPy


async def main():
    async with TikTokPy() as bot:
        await bot.follow("noor725151")
        items = await bot.user_feed(username="noor725151", amount=5)
        for item in items:
            await bot.like(item)

asyncio.run(main())
