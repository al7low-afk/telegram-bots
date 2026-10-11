import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio

# يقرأ التوكن تلقائياً من المتغيرات في Render
TOKEN = os.getenv("TIKTOK_BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

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
        
        # ترويسة المتصفح لمنع حظر 403
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

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
