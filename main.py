import os
import subprocess
from aiohttp import web

async def handle(request):
    return web.Response(text="Bots are running 24/7!")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.0(os.environ.get("PORT", 10000)))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

def main():
    p1 = subprocess.Popen(["python", "tiktok_bot.py"])
    p2 = subprocess.Popen(["python", "azkar_bot.py"])

    import asyncio
    asyncio.run(start_web_server())

if __name__ == "__main__":
    main()
