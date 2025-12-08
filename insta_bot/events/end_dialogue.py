from ai_service import generate_response, run_with_retry


def handle_end_dialogue(cl, user_id, user_text):
    end_dialogue_text = ("""
        Спасибо за обращение! Ваша заявка принята и будет рассмотрена в ближайшее время.
        Скоро мы свяжемся с вами. Будьте здоровы!
    """)


    parting_text = f"""
        Определи, на каком языке написан этот текст пользователя: {user_text}.
        Возьми мой текст и переведи/адаптируй его так, чтобы он звучал естественно на том же языке.  

        Правила:
        Всегда обращайся к пользователю на «Вы».  
        Не добавляй никаких флагов, эмодзи или украшений, которых нет в оригинальном тексте.  
        Сохраняй нейтральный и вежливый тон.  

        Текст для перевода: {end_dialogue_text}
    """

    reply_text = run_with_retry(generate_response, parting_text, retries=8)
    run_with_retry(cl.direct_send, reply_text, [user_id], retries=8)

