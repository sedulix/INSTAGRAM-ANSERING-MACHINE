from ai_service import generate_response


# ASK SERVICE MESSAGE ------------------------------------------------------------------------------------------------<<


def send_service_question(cl, user_id, user_text):
    # SERVICE QUESTION
    prompt = (f"""
            Поблагодари за номер телефона и задай наводящий вопрос: что интересует — бронирование или цена?
            Отвечай на том же языке, на котором пользователь пишет.
            Пример текста пользователя: {user_text}
       """)
    cl.direct_send(generate_response(prompt), [user_id])

