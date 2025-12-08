from instagrapi import Client
from pathlib import Path
import json
import time

from data_requests import LeadDB, SeenMessages
from router import route_thread


# DB OBJECTS ---------------------------------------------------------------------------------------------------------->
L_db = LeadDB()
SEEN_db = SeenMessages()


# CLIENT OBJECT AND SAFE LOGIN INFORMATION ---------------------------------------------------------------------------->
cl = Client()

SESSION_PATH = Path("json_files/session.json")
LOGIN_PATH = Path("json_files/login.json")


# SAFE LOGIN INFO ---------------------------------------------------------------------------------------------------->>


def save_state(login_info):
    with open(LOGIN_PATH, "w") as f:
        json.dump(login_info, f)


# LOADING LOGIN INFO ------------------------------------------------------------------------------------------------->>


def load_state():
    try:
        with open(LOGIN_PATH, "r") as f:
            return json.load(f)

    except FileNotFoundError:
        return {"username": "", "password": "", "chat_id": ""}


# LOGIN INTO BOT SESSION --------------------------------------------------------------------------------------------->>


def login_bot():
    if SESSION_PATH.exists():
        cl.load_settings(SESSION_PATH)

    try:
        if LOGIN_PATH.exists():
            f = load_state()
            cl.login(f.get("username"), f.get("password"))
            cl.dump_settings(SESSION_PATH)
            print("Вход выполнен")

        else:
            username1 = input("Введите ваш логин от Instagram: ")
            password2 = input("Введите пароль: ")
            login1 = input("Введите ID вашего чата: ")

            state = load_state()
            state["username"] = username1
            save_state(state)

            state1 = load_state()
            state1["password"] = password2
            save_state(state1)

            state2 = load_state()
            state2["chat_id"] = login1
            save_state(state2)

            cl.login(username1, password2)
            print("Вход выполнен")
            print("BOT ID:", cl.user_id)


    except Exception as e:
        print(f"[ERROR]: {e}")


# LAUNCHING INSTAGRAM BOT ------------------------------------------------------------------------------------------->>>


def start_loop_bot():
    bot_user_id = cl.user_id
    print(f"BOT ID: {bot_user_id}")

    while True:
        try:
            threads = cl.direct_threads(amount=20)
            print(f"[DEBUG] Found {len(threads)} threads")

            for thread in threads:
                print(f"[DEBUG] Processing thread {thread.id}")
                route_thread(cl, L_db, SEEN_db, thread, bot_user_id)

        except Exception as e:
            print(f"[ERROR]: {e}")

        time.sleep(30)

