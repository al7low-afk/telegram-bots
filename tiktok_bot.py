import asyncio
import html
import logging
import re
import shutil
import tempfile
from pathlib import Path

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError, TelegramRetryAfter
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, InputMediaPhoto, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = "8695837050:AAExHFXN2BFh9rcc6aArRgawOU-74tdc0js"
REQUIRED_CHANNEL = "@azkar201"
SIGN = "📥 @z3dlbot"
CAPTION_LIMIT = 1024
TEXT_LIMIT = 4096
MAX_UPLOAD = 50 * 1024 * 1024
MAX_PARALLEL = 3

URL_RE = re.compile(r"https?://(?:[a-z0-9-]+\.)*(?:tiktok\.com|vt\.tiktok\.com)/\S+", re.I)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger("TikTokBot")

dp = Dispatcher()
SEM = asyncio.Semaphore(MAX_PARALLEL)

async def with_retry(fn, *args, **kwargs):
    for attempt in range(4):
        try:
            return await fn(*args, **kwargs)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
        except TelegramNetworkError:
            if attempt == 3: raise
            await asyncio.sleep(2 * (attempt + 1))
    raise RuntimeError("Telegram request failed after retries")

async def check_user_subscription(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        log.error(f"Subscription check error: {e}")
        return False

def get_sub_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 اشترك في القناة الآن", url=f"https://t.me/{REQUIRED_CHANNEL.replace('@', '')}")
    builder.button(text="✅ تحقق من الاشتراك", callback_data="check_sub")
    builder.adjust(1)
    return builder.as_markup()

def build_caption(desc: str | None) -> tuple[str, bool]:
    desc = (desc or "").strip()
    tail = f"\n\n{SIGN}"
    text, overflow = desc, False
    while len(html.escape(text)) + len(tail) + (1 if overflow else 0) > CAPTION_LIMIT:
        overflow = True
        text = text[: int(len(text) * 0.9)].rstrip()
    return (html.escape(text) + ("…" if overflow else "") + tail).strip(), overflow

async def download_file(http: aiohttp.ClientSession, url: str, path: Path) -> Path:
    async with http.get(url, timeout=aiohttp.ClientTimeout(total=60)) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            async for chunk in r.content.iter_chunked(64 * 1024):
                f.write(chunk)
    return path

async def process(message: Message, url: str):
    if not await check_user_subscription(message.bot, message.from_user.id):
        await message.answer("⚠️ **عذراً، يجب عليك الاشتراك في القناة أولاً لكي تتمكن من استخدام البوت!**", reply_markup=get_sub_keyboard())
        return

    status = await message.reply("⏳ جاري التحميل...")
    tmp = Path(tempfile.mkdtemp(prefix="z3dl_"))
    try:
        async with SEM:
            api_url = f"https://www.tikwm.com/api/?url={url}"
            async with aiohttp.ClientSession() as http:
                async with http.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    res_json = await resp.json()

                if res_json.get("code") != 0:
                    await message.reply("❌ تعذر جلب البيانات من الرابط.")
                    return

                data = res_json.get("data", {})
                caption, overflow = build_caption(data.get("title") or "")

                images = data.get("images", [])
                if images:
                    paths = []
                    for i, img_url in enumerate(images[:10]):
                        p = tmp / f"img_{i:02d}.jpg"
                        await download_file(http, img_url, p)
                        paths.append(p)

                    if paths:
                        for start in range(0, len(paths), 10):
                            chunk = paths[start : start + 10]
                            cap = caption if start == 0 else None
                            if len(chunk) == 1:
                                await with_retry(message.answer_photo, FSInputFile(chunk[0]), caption=cap)
                            else:
                                media = [InputMediaPhoto(media=FSInputFile(p), caption=cap if j == 0 else None) for j, p in enumerate(chunk)]
                                await with_retry(message.answer_media_group, media)
                        return

                video_url = data.get("play")
                if video_url:
                    video_path = tmp / "video.mp4"
                    await download_file(http, video_url, video_path)
                    if video_path.stat().st_size <= MAX_UPLOAD:
                        await with_retry(message.answer_video, FSInputFile(video_path), caption=caption, supports_streaming=True)
                    else:
                        await message.reply("⚠️ حجم الفيديو أكبر من 50MB.")
    except Exception as e:
        log.exception("Error: %s", e)
        await message.reply("❌ حدث خطأ أثناء التحميل.")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        try: await status.delete()
        except Exception: pass

@dp.callback_query(F.data == "check_sub")
async def verify_subscription(callback: CallbackQuery):
    if await check_user_subscription(callback.bot, callback.from_user.id):
        await callback.message.edit_text("✅ تم التحقق من اشتراكك بنجاح! أرسل لي رابط تيك توك وسأقوم بتحميله فوراً 🚀")
    else:
        await callback.answer("❌ لم تقم بالاشتراك في القناة بعد!", show_alert=True)

@dp.message(CommandStart())
async def start(message: Message):
    if not await check_user_subscription(message.bot, message.from_user.id):
        await message.answer("أهلاً بك في بوت تحميل تيك توك! 🚀\n\n⚠️ اشترك في القناة لاستخدام البوت:", reply_markup=get_sub_keyboard())
    else:
        await message.answer("أهلاً بك! أرسل لي أي رابط تيك توك وسأقوم بتحميله فوراً 🔗")

@dp.message(F.text.regexp(URL_RE))
async def on_link(message: Message):
    m = URL_RE.search(message.text or "")
    if m: await process(message, m.group(0).rstrip(".,)"))

@dp.message(F.text)
async def other(message: Message):
    if not await check_user_subscription(message.bot, message.from_user.id):
        await message.answer("⚠️ يجب عليك الاشتراك في القناة أولاً:", reply_markup=get_sub_keyboard())
    else:
        await message.answer("أرسل رابط تيك توك صحيح 🔗")

async def main():
    bot = Bot(BOT_TOKEN, session=AiohttpSession(timeout=300), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())