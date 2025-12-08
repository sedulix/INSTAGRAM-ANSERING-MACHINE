import asyncio

from data_base_sql import LeadDB, SeenMessages
from insta_bot import login_bot, start_loop_bot
from tg_bot import run_telegram_bot


leads = LeadDB()
messages = SeenMessages()


async def main():
    print("\n[1] Запуск Telegram-бота...")
    tg_task = asyncio.create_task(run_telegram_bot())

    print("[2] Инициализация Instagram-бота...")
    try:
        login_bot()
        print("[3] login_bot() выполнен")

        leads.init_db()
        messages.init_db()
        print("[4] init_db() выполнен")

        asyncio.create_task(asyncio.to_thread(start_loop_bot))
        print("[5] start_loop_bot() выполнен")

    except Exception as e:
        print(f"[ERROR] Instagram-бот: {e}")

    await tg_task
    print("[6] Telegram-бот будет ждать...")


if __name__ == "__main__":
    print("[0] Старт программы")
    asyncio.run(main())


