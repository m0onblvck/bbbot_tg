from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus
from config import BOT_TOKEN, CHANNEL_USERNAME, CHANNEL_ID
import asyncio


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def check_membership(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in {
            'member',
            'administrator',
            'creator'
        }
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False

# async def check_membership(user_id: int) -> bool:
#     try:
#         member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
#         return member.status in {
#             ChatMemberStatus.MEMBER,
#             ChatMemberStatus.ADMINISTRATOR,
#             ChatMemberStatus.OWNER,
#         }
#     except Exception as e:
#         print(f"Ошибка проверки подписки: {e}")
#         return False


@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_group_message(message: Message):
    user_id = message.from_user.id
    is_member = await check_membership(user_id)

    if not is_member:
        try:
            await message.delete()
            invite_link = f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"
            await message.answer(

                 f"👋 Привет, <a href='tg://user?id={user_id}'>котик</a>! Ты ещё не подписался на наш канал с крутыми референсами? Без подписки рисовать будет сложно! 😿\n Подпишись, чтобы вдохновляться и творить вместе! 👉 <a href='{invite_link}'>канал</a>",
                parse_mode="HTML",
            )
        except Exception as e:
            print(f"Ошибка при удалении или ответе: {e}")


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
