import logging

from ai_moderation_bot.config import TELEGRAM_TOKEN

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F
import asyncio

from ai_moderation_bot.db_models import ContentBlocked, ContentAllowed, TgUsers
from ai_moderation_bot.services import analyze_content, insert_into_db

logging.basicConfig(filename='AIModerationBot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command(commands=["start"]))
async def start(message: Message):
    await message.answer("I am your assistant in content analysis")

@dp.message(F.text)
async def handle_sms(message: Message):
    sms_text = message.text
    nickname = message.from_user.username
    tg_user = TgUsers(nickname=nickname)
    insert_into_db(tg_user)
    if not analyze_content(sms_text):
        content = ContentBlocked(tg_users_nickname=nickname, text=sms_text)
        await message.reply("Sorry, this message has been blocked due to foul language.")
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    else:
        content = ContentAllowed(tg_users_nickname=nickname, text=sms_text)

    insert_into_db(content)

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())