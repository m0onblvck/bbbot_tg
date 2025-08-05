import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

# Загружаем переменные среды
load_dotenv()

# Переменные из .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = "/webhook"

# Бот и диспетчер
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Проверка подписки
async def check_membership(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in {
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR,
        }
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False

# Обработка сообщений в группе
@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_group_message(message: Message):
    user_id = message.from_user.id
    is_member = await check_membership(user_id)

    if not is_member:
        try:
            await message.delete()
            invite_link = f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"
            await message.answer(
                f"👋 Привет, <a href='tg://user?id={user_id}'>котик</a>! Ты ещё не подписался на наш канал с крутыми референсами? Без подписки рисовать будет сложно! 😿\nПодпишись 👉 <a href='{invite_link}'>канал</a>",
            )
        except Exception as e:
            print(f"Ошибка при удалении или ответе: {e}")

# Установка и удаление webhook (без bot аргумента!)
async def on_startup(dispatcher: Dispatcher):
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    print("Webhook установлен.")

async def on_shutdown(dispatcher: Dispatcher):
    await bot.delete_webhook()
    print("Webhook удалён.")

# Запуск aiohttp сервера
async def main():
    app = web.Application()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp)

    return app

if __name__ == "__main__":
    web.run_app(main(), port=8080)
