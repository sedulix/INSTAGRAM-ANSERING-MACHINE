from ai_service import generate_response, run_with_retry


def handle_following_question(cl, user_id, user_text):
    following_question_message = (
        "Хотите ли вы задать еще какие-то вопросы?"
        "Например, про бронирование, стоимость или процедуры?"
    )

    prompt = f"""
        Определи, на каком языке написан этот текст пользователя: {user_text}.
        Возьми мой текст и переведи/адаптируй его так, чтобы он звучал естественно на том же языке.  

        Правила:
        Всегда обращайся к пользователю на «Вы».  
        Сохраняй нейтральный и вежливый тон.  
        Можешь немного изменять текст для разнообразности но не меняй сам смысл текста

        Текст для перевода: {following_question_message}
"""

    reply_text = run_with_retry(generate_response, prompt, retries=8)
    run_with_retry(cl.direct_send, reply_text, [user_id], retries=8)
