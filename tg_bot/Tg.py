import asyncio
import logging
import json
import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data_requests import LeadDB, SeenMessages


# LOADING ENV DATA ---------------------------------------------------------------------------------------------------->
load_dotenv()


# DB MANAGER OBJECT --------------------------------------------------------------------------------------------------->
db = LeadDB()
seen_db = SeenMessages()


# PATH FILES ---------------------------------------------------------------------------------------------------------->
json_file = "json_files/state.json"
CONFIG_FILE = "json_files/login.json"


# BOT INITIALIZATION ------------------------------------------------------------------------------------------------->>
dp = Dispatcher()
bot = Bot(token=os.getenv("BOT_TOKEN"))

logging.basicConfig(level=logging.INFO)
builder = InlineKeyboardBuilder()


# LOAD REPEATED MSG ID ------------------------------------------------------------------------------------------------>


def load_state():
    try:
        with open(json_file, "r") as f:
            return json.load(f)

    except FileNotFoundError:
        return {"known_ids": [], "current_index": {}}


def save_state(state):
    with open(json_file, "w") as f:
        json.dump(state, f)


def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    except FileNotFoundError:
        return {"chat_id": 0}


# KEYBOARD DEFINITION ------------------------------------------------------------------------------------------------>>


def status_keyboard(lead_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сменить статус", callback_data=f"switch:{lead_id}")]
    ])
    return keyboard


# CATCHING PHONE NUMBERS -------------------------------------------------------------------------------------------->>>


async def send_new_leads():
    state = load_state()
    known_ids = set(map(str, state["known_ids"]))

    while True:
        leads = db.get_leads()
        print(leads)

        for lead in leads:
            if lead[0] not in known_ids:
                phone = lead[2]
                service = lead[4]

                if not phone or service:
                    continue

                else:
                    status = "рассмотрена" if lead[3] else "не рассмотрена"
                    config = load_config()
                    chat_id = config.get("chat_id")

                    await bot.send_message(chat_id,
                                        f"Номер телефона: {phone}\n"
                                            f"Услуга: {service}"
                                            f"\nСтатус заявки - {status}", reply_markup=status_keyboard(lead[0]))

                    known_ids.add(lead[0])
                    state["known_ids"] = list(known_ids)

                    save_state(state)

        await asyncio.sleep(10)


# COMMANDS HANDLERS ------------------------------------------------------------------------------------------------->>>


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    state = load_state()
    state["current_index"][str(message.from_user.id)] = 0
    save_state(state)
    await message.answer("Бот запущен и следит за заявками.")


@dp.callback_query(lambda c: c.data.startswith("switch:"))
async def switch_text(callback_query: types.CallbackQuery):

    parts = callback_query.data.split(":")
    if len(parts) > 1:
        lead_id = int(parts[1])
        db.delete_user(lead_id)

        await callback_query.answer()

        state = load_state()
        user_id = str(callback_query.from_user.id)
        index = state["current_index"].get(user_id, 0)
        new_index = 1 - index
        state["current_index"][user_id] = new_index
        save_state(state)

        await callback_query.message.edit_text(f"Заявка рассмотрена", reply_markup=status_keyboard(lead_id))

    else:
        await callback_query.answer("[CALLBACK ERROR]: Неверный формат callback_data.")


# LAUNCH THE TG_BOT ------------------------------------------------------------------------------------------------->>>


async def run_telegram_bot():
    db.init_db()
    seen_db.init_db()

    asyncio.create_task(send_new_leads())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_telegram_bot())


