import os, time

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam
)

# LOAD ENV VARIABLES --------------------------------------------------------------------------------------------------<

load_dotenv()

# TOKENS --------------------------------------------------------------------------------------------------------------<

API_TOKEN = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")

# CLIENT OBJECT -------------------------------------------------------------------------------------------------------<

client = OpenAI(api_key=API_TOKEN, base_url="https://openrouter.ai/api/v1")


# RETRYING REQUESTS -------------------------------------------------------------------------------------------------<<<


def run_with_retry(func, *args, retries=8, **kwargs):
    for attempt in range(1, retries + 1):
        try:
            print(f"[RETRY DEBUG]: attempt={attempt}/{retries}, func={func.__name__}, args={args}, kwargs={kwargs}")

            result = func(*args, **kwargs)

            print(f"[RETRY DEBUG]: attempt={attempt}: success, got result={result!r}")
            return result

        except Exception as e:
            err = str(e)
            print(f"[RETRY DEBUG]: attempt={attempt}: error={err}")

            delay = 40

            if attempt < retries:
                print(f"[RETRY DEBUG:] waiting {delay}s before retry...")
                time.sleep(delay)
                continue

    print(f"[RETRY DEBUG]: {func.__name__} failed after {retries} attempts")
    return "unknown" if func.__name__ == "classify_intent" else None


# GENERATE RESPONSE -------------------------------------------------------------------------------------------------->>


def generate_response(prompt: str) -> str:
    try:
        messages: list[ChatCompletionMessageParam] = [ChatCompletionSystemMessageParam(
            role="system",
            content=("""
                Ты Instagram-бот компании Fanat.
                Отвечай только конечным текстом для клиента, без комментариев и пояснений.
                Форматируй красиво: эмодзи, абзацы, списки.
                Отвечай всегда на языке пользователя.
                Не упоминай, что ты ИИ.
            """)),

            ChatCompletionUserMessageParam(
                role = "user",
                content = prompt)]

        response = client.chat.completions.create(
            model = MODEL,
            messages = messages,
            temperature = 0.2
        )

        msg = response.choices[0].message
        if isinstance(msg.content, list):
            result = "".join([c["text"] for c in msg.content if c["type"] == "text"]).strip()
        else:
            result = msg.content.strip()
        return result

    except Exception as e:
        print(f"[AI REQUEST ERROR]: {e}")
        return ""


# CLASSIFY SERVICE ---------------------------------------------------------------------------------------------------<<


def classify_intent(user_text: str):
    try:
        messages: list[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(
                role="system",
                content=("""
                    Классифицируй намерение пользователя строго одним словом:
                    'booking' - если он хочет забронировать место/услугу
                    'price' - если он спрашивает про цены/стоимость
                    'treatment' - если он интересуется лечением
                    'no_more_questions' - если пользователь ответил тем что узнал все что хотел или ему больше ничего не надо
                    'unknown' - если не подходит ни один вариант
                    Никаких пояснений, только одно слово.
                """)),
            ChatCompletionUserMessageParam(
                role="user",
                content=user_text
            )
        ]

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0
        )

        result = response.choices[0].message.content.strip()
        if result in ["booking", "price", "treatment", "no_more_questions"]:
            return result
        return "unknown"

    except Exception as e:
        print(f"[AI REQUEST ERROR (classify_intent)]: {e}")
        return "unknown"

