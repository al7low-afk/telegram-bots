import asyncio
import datetime
import logging
import random
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

# التوكن الخاص ببوت الأذكار الجديد @azkar888bot
AZKAR_BOT_TOKEN = "8969387100:AAHv_23YWJKMjbu_FVss-CD68I20weis0"
CHANNEL_ID = "@azkar201"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger("AzkarBot")

dp = Dispatcher()

MORNING_AZKAR = [
    (
        "☀️ **أذكار الصباح (أصبحنا وأصبح الملك لله):**\n\n"
        "«أَصْبَحْنَا وَأَصْبَحَ المُلْكُ لِلَّهِ، وَالحَمْدُ لِلَّهِ، لا إِلهَ إِلاَّ اللَّهُ وَحْدَهُ لا شَرِيكَ لَهُ، لَهُ المُلْكُ وَلَهُ الحَمْدُ وَهُوَ عَلى كُلِّ شَيْءٍ قَدِيرٌ».\n\n"
        "🌿 *رَبِّ أَسْأَلُكَ خَيْرَ ما في هَذَا الْيَوْمِ وَخَيْرَ ما بَعْدَهُ*."
    ),
    (
        "🌸 **سيد الاستغفار (للصباح):**\n\n"
        "«اللَّهُمَّ أَنْتَ رَبِّي لا إله إلا أنت خلقتني وأنا عبدك، وأنا على عهدك ووعدك ما استطعت، أعوذ بك من شر ما صنعت، أبوء لك بنعمتك علي، وأبوء لك بذنبي فاغفر لي، فإنه لا يغفر الذنوب إلا أنت»."
    )
]

EVENING_AZKAR = [
    (
        "🌙 **أذكار المساء (أمسينا وأمسَى الملك لله):**\n\n"
        "«أَمْسَيْنَا وَأَمْسَى المُلْكُ لِلَّهِ، وَالحَمْدُ لِلَّهِ، لا إِلهَ إِلاَّ اللَّهُ وَحْدَهُ لا شَرِيكَ لَهُ، لَهُ المُلْكُ وَلَهُ الحَمْدُ وَهُوَ عَلى كُلِّ شَيْءٍ قَدِيرٌ».\n\n"
        "✨ *رَبِّ أَسْأَلُكَ خَيْرَ ما في هَذِهِ اللَّيْلَةِ وَخَيْرَ ما بَعْدَها*."
    ),
    (
        "🤍 **آية الكرسي والتحصين:**\n\n"
        "«اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ...»"
    )
]

async def azkar_scheduler(bot: Bot):
    last_morning_date = None
    last_evening_date = None
    
    log.info("بدأت جدولة الأذكار التلقائية...")
    
    while True:
        now = datetime.datetime.now()
        cur_date = now.date()
        cur_hour = now.hour
        cur_min = now.minute

        # أذكار الصباح الساعة 6:00 صباحاً
        if cur_hour == 6 and cur_min == 0 and last_morning_date != cur_date:
            try:
                text = random.choice(MORNING_AZKAR) + "\n\n📖 قناة الأذكار (@azkar201)"
                await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode=ParseMode.MARKDOWN)
                last_morning_date = cur_date
                log.info("تم إرسال أذكار الصباح بنجاح.")
            except Exception as e:
                log.error(f"خطأ في أذكار الصباح: {e}")

        # أذكار المساء الساعة 5:00 عصراً (17:00)
        if cur_hour == 17 and cur_min == 0 and last_evening_date != cur_date:
            try:
                text = random.choice(EVENING_AZKAR) + "\n\n📖 قناة الأذكار (@azkar201)"
                await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode=ParseMode.MARKDOWN)
                last_evening_date = cur_date
                log.info("تم إرسال أذكار المساء بنجاح.")
            except Exception as e:
                log.error(f"خطأ في أذكار المساء: {e}")

        await asyncio.sleep(30)

async def main():
    bot = Bot(
        AZKAR_BOT_TOKEN,
        session=AiohttpSession(timeout=300),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await bot.delete_webhook(drop_pending_updates=True)
    
    # تشغيل جدولة الأذكار في الخلفية
    asyncio.create_task(azkar_scheduler(bot))
    
    log.info("بوت الأذكار (@azkar888bot) يعمل الآن...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())