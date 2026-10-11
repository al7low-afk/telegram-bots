
import os
import asyncio
import logging
from urllib.parse import urlparse

import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TIKTOK_BOT_TOKEN")
PORT = int(os.getenv("PORT", "10000"))

if not TOKEN:
    raise RuntimeError(
        "متغير TIKTOK_BOT_TOKEN غير موجود في Render Environment"
    )

bot = Bot(token=TOKEN)
dp = Dispatcher()

HTTP_TIMEOUT = aiohttp.ClientTimeout(total=25)


# سيرفر ويب مطلوب لخدمة Render Web Service
async def health(request):
    return web.json_response({
        "status": "ok",
        "service": "TikTok Telegram Bot"
    })


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        host="0.0.0.0",
        port=PORT
    )
    await site.start()

    logger.info("Web server started on port %s", PORT)
    return runner


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "أهلاً بك في بوت تحميل تيك توك! 🚀\n\n"
        "أرسل رابط مقطع تيك توك وسأحاول تحميله لك."
    )


@dp.message()
async def download_tiktok(message: types.Message):
    url = (message.text or "").strip()

    if not url:
        await message.answer("أرسل رابط تيك توك كنص.")
        return

    try:
        parsed = urlparse(url)

        if (
            parsed.scheme not in ("http", "https")
            or not parsed.hostname
            or not (
                parsed.hostname == "tiktok.com"
                or parsed.hostname.endswith(".tiktok.com")
            )
        ):
            await message.answer("⚠️ أرسل رابط تيك توك صحيحًا.")
            return

        status_message = await message.answer(
            "جاري محاولة تحميل المقطع... ⏳"
        )

        api_url = "https://www.tikwm.com/api/"

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
        }

        async with aiohttp.ClientSession(
            timeout=HTTP_TIMEOUT,
            headers=headers
        ) as session:
            async with session.get(
                api_url,
                params={"url": url},
            ) as response:

                if response.status != 200:
                    logger.warning(
                        "Tikwm returned HTTP %s",
                        response.status
                    )
                    await status_message.edit_text(
                        "تعذر التحميل؛ خدمة Tikwm رفضت الطلب "
                        f"(HTTP {response.status}). جرّب لاحقًا."
                    )
                    return

                try:
                    result = await response.json()
                except (aiohttp.ContentTypeError, ValueError):
                    logger.warning(
                        "Tikwm returned a non-JSON response"
                    )
                    await status_message.edit_text(
                        "خدمة التحميل رجعت استجابة غير صالحة. "
                        "جرّب لاحقًا."
                    )
                    return

        if result.get("code") != 0:
            await status_message.edit_text(
                "لم أتمكن من تحميل المقطع. "
                "قد يكون الرابط غير متاح أو الخدمة متوقفة."
            )
            return

        data = result.get("data") or {}
        video_url = data.get("play")

        if not video_url:
            await status_message.edit_text(
                "لم يتم العثور على رابط الفيديو."
            )
            return

        await status_message.edit_text(
            "تم تجهيز المقطع، جاري إرساله... 📤"
        )

        await message.answer_video(
            video=video_url,
            caption="تم التحميل بواسطة بوتك 🚀"
        )

        await status_message.delete()

    except asyncio.TimeoutError:
        logger.warning("TikTok request timed out")
        await message.answer(
            "انتهت مهلة الاتصال. جرّب مرة أخرى."
        )

    except Exception:
        logger.exception("Error processing TikTok URL")
        await message.answer(
            "حدث خطأ أثناء التحميل أو إرسال الفيديو. "
            "جرّب مرة أخرى لاحقًا."
        )


async def main():
    runner = None

    try:
        # يتحقق من التوكن قبل بدء الخدمة
        await bot.get_me()

        runner = await start_web_server()

        logger.info("Bot started successfully")

        await dp.start_polling(bot)

    finally:
        if runner is not None:
            await runner.cleanup()

        await bot.session.close()
        logger.info("Bot connections closed")


if __name__ == "__main__":
    asyncio.run(main())
