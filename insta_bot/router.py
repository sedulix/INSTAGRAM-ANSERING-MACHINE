from ai_service import classify_intent, run_with_retry
from events import (
    handle_greeting,
    handle_ask_number,
    handle_ask_price,
    handle_ask_treatment,
    handle_following_question,
    handle_end_dialogue,
    thank_and_inform
)


# SAFE MESSAGE SEND ------------------------------------------------------------------------------------------------->>>


def _safe_send_text(cl, thread, text: str):
    try:
        if getattr(thread, "pending", False):
            cl.direct_thread_approve(thread.id)
        cl.direct_send(text, thread_ids=[thread.id])

    except Exception as e:
        print(f"[DIRECT_SEND ERROR]: thread_id={thread.id}]: {e}", flush=True)
        return


# EVENTS HANDLER ----------------------------------------------------------------------------------------------------<<<


def route_thread(cl, L_db, SEEN_db, thread, bot_user_id):
    user_messages = [m for m in thread.messages if str(m.user_id) != str(bot_user_id)]
    if not user_messages:
        print(f"[SKIP]: empty thread {thread.id}")
        return

    last_message = max(user_messages, key=lambda m: m.timestamp)
    last_seen_id = SEEN_db.get_last_message_id(thread.id)
    user_id = last_message.user_id

    if last_seen_id and str(last_message.id) == str(last_seen_id):
        print(f"[SKIP]: already seen message_id={last_message.id} thread_id={thread.id}")
        return

    print(f"[HANDLED]: new message_id={last_message.id} text={last_message.text}")


    try:

        # GREETING PART --------------------------------------------------------------------------------------------->>>
        if not L_db.user_exists(user_id):
            print(f"[DEBUG]: new user detected {user_id}")

            try:
                handle_greeting(cl, user_id, last_message.text)
                L_db.insert_user(user_id, stage="waiting_question")

            except Exception as e:
                print(f"[HANDLE GETTING ERROR]: {e}")
                _safe_send_text(cl, thread, "Извините 🙏 Сейчас технические неполадки напишите чуть позже")
            return

        stage = L_db.get_stage(user_id)
        print(f"[DEBUG]: user_id={user_id}, stage={stage}")


        # DIALOGUE LOGIC -------------------------------------------------------------------------------------------->>>


        if stage == "waiting_question":

            try:
                print(f"[PRECALL]: classify_intent={classify_intent}, type={type(classify_intent)}")
                intent = run_with_retry(classify_intent, last_message.text)
                print(f"[DEBUG]: classified intent={intent}")

            except Exception as e:
                _safe_send_text(cl, thread,"Извините 🙏 Сейчас технические неполадки напишите чуть позже")
                print(f"[AI REQUEST ERROR]: {e}")
                return

            if intent == "booking":
                if L_db.get_service(user_id):
                    _safe_send_text(cl, thread, "Вы уже оставили заявку, скоро мы с вами свяжемся! 📞")

                L_db.save_service(user_id, "booking")
                handle_ask_number(cl, user_id, L_db, last_message)

                L_db.update_stage("waiting_phone", user_id)
                print("[STAGE]: updated stage: waiting_phone")
                return

            if intent == "price":
                handle_ask_price(cl, user_id)
                handle_following_question(cl, user_id, last_message.text)
                L_db.update_stage("waiting_followup", user_id)
                return

            if intent == "treatment":
                handle_ask_treatment(cl, user_id)
                handle_following_question(cl, user_id, last_message.text)
                L_db.update_stage("waiting_followup", user_id)
                return

            if intent == "unknown":
                _safe_send_text(cl, thread,"Не совсем вас понял. Подскажите, вас интересует бронирование или цена?")
                return


        # CATCHING IF USER WANT'S TO ASK SOMETHING ELSE ------------------------------------------------------------->>>


        if stage == "waiting_followup":

            try:
                intent = run_with_retry(classify_intent, last_message.text)
                print(f"[DEBUG][followup] classified intent={intent}")

            except Exception as e:
                _safe_send_text(cl, thread, "Извините 🙏 Сейчас технические неполадки, напишите чуть позже")
                print(f"[AI REQUEST ERROR][followup]: {e}")
                return

            if intent == "no_more_questions":
                L_db.update_stage("", user_id)
                print("[STAGE][followup] updated stage: end_dialogue")

                handle_end_dialogue(cl, user_id, last_message.text)
                cl.direct_thread_delete(thread.id)
                return

            if intent == "booking":
                if L_db.get_service(user_id):
                    _safe_send_text(cl, thread, "Вы уже оставили заявку, скоро мы с вами свяжемся 📞")

                L_db.save_service(user_id, "booking")
                handle_ask_number(cl, user_id, L_db, last_message)

                L_db.update_stage("waiting_phone", user_id)
                print("[STAGE][followup] updated stage: waiting_phone")
                return

            if intent == "price":
                handle_ask_price(cl, user_id)
                handle_following_question(cl, user_id, last_message.text)
                return

            if intent == "treatment":
                handle_ask_treatment(cl, user_id)
                handle_following_question(cl, user_id, last_message.text)
                return

            if intent == "unknown":
                _safe_send_text(cl, thread, "Не совсем понял. Подскажите, вас интересует бронирование, цена "
                                            "или лечение?")
                return


        # ONLY FROM BOOKING STAGE -----------------------------------------------------------------------------------<<<

        if stage == "waiting_phone":

            try:
                phone = (last_message.text or "").strip()

                if not phone:
                    prev_messages = [m for m in user_messages if m.id != last_message.id]

                    if prev_messages:
                        prev_message = max(prev_messages, key=lambda m: m.timestamp)
                        phone = (prev_message.text or "").strip()

                if not phone:
                    _safe_send_text(cl, thread, "Пожалуйста, напишите номер телефона цифрами 📞")
                    return

                L_db.save_phone_number(user_id, phone)
                L_db.update_stage("waiting_followup", user_id)

                thank_and_inform(cl, user_id, last_message.text)
                handle_following_question(cl, user_id, last_message.text)

                print(f"[DEBUG] saved phone={phone} for user_id={user_id}")

            except Exception as e:
                print(f"[PHONE ERROR]: {e}")


# SAVING LAST MESSAGE -----------------------------------------------------------------------------------------------<<<

    except Exception as e:
        print(f"[HANDLE ERROR]: {e}")

    finally:
        SEEN_db.save_last_message_id(thread.id, last_message.id)

