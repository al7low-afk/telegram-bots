import os
import aiohttp
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# قراءة التوكن من إعدادات Render
TOKEN = os.getenv("TIKTOK_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- إعدادات سيرفر الويب لإرضاء منصة Render ---
async def handle(request):
    return web.Response(text="TikTok Bot is running 24/7!")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- أوامر بوت تيليجرام ---
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("أهلاً بك في بوت تحميل تيك توك! 🚀\nأرسل أي رابط تيك توك وسأقوم بتحميله فوراً.")

@dp.message()
async def download_tiktok(message: types.Message):
    url = message.text
    if "tiktok.com" not in url:
        await message.answer("⚠️ أرسل رابط تيك توك صحيح 🔗")
        return

    await message.answer("جاري التحميل... ⏳")
    
    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as resp:
                data = await resp.json()
                
                if data.get("code") == 0:
                    video_url = data["data"]["play"]
                    await message.answer_video(video=video_url, caption="تم التحميل بنجاح بواسطة بوتك 🚀")
                else:
                    await message.answer("❌ حدث خطأ أثناء التحميل.")
    except Exception as e:
        await message.answer("❌ حدث خطأ أثناء التحميل.")

# --- التشغيل الأساسي ---
async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
