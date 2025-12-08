from .ask_service import send_service_question
from ai_service import generate_response, run_with_retry

# EXTRACT PHONE ------------------------------------------------------------------------------------------------------>>


def extract_phone(message):
    try:
        if getattr(message, "contact", None) and getattr(message.contact, "phone_number", None):
            return (message.contact.phone_number or "").strip()
        elif message.type == "none":
            return message[1].text.strip()
        elif getattr(message, "text", None):
            return (message.text or "").strip()

    except Exception as e:
        print(f"[extract_phone error] {e}")

    return ""


# PHONE VALIDATION ---------------------------------------------------------------------------------------------------<<


def check_phone_validation(text):
    if not text:
        return False

    t = text.strip().replace(" ", "")
    return t.isdigit() and 7 <= len(t) <= 20


# ASK PHONE NUMBER ---------------------------------------------------------------------------------------------------<<


def handle_ask_number(cl, user_id, L_db, message):
    cur = extract_phone(message)

    if check_phone_validation(cur):
        L_db.save_phone_number(user_id, cur)
        send_service_question(cl, user_id, cur)
        return

    ask_phone_prompt = ("""
        Правила:
        Без приветствия попроси прислать номер телефон с плюсом в начале и без пробелов.
        Отвечай на том же языке на каком тебе написали.
        Всегда обращайся к пользователю на «Вы».  
        Не меняй смысл текста.
        В виде примера приведи шаблон для номера телефона: +999887776611
    """)

    reply_text = run_with_retry(generate_response, ask_phone_prompt, retries=8)
    run_with_retry(cl.direct_send, reply_text, [user_id], retries=8)


# END ASK_PHONE STAGE AND INFORM -------------------------------------------------------------------------------------<<


def thank_and_inform(cl, user_id, user_text):
    inform_prompt = (f"""
        Правила:
        Поблагодари пользователя за оставленную заявку и скажи что менеджер скоро с ним свяжется
        Всегда обращайся к пользователю на «Вы».  
        Сохраняй нейтральный и вежливый тон.  
        Не меняй смысл текста.  
        Без прощальных предложений.
        Пример текста пользователя: {user_text}
    """)

    reply_text = run_with_retry(generate_response, inform_prompt, retries=8)
    run_with_retry(cl.direct_send, reply_text, [user_id], retries=8)

