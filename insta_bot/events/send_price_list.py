import os


# SEND PRICE LIST PHOTO --------------------------------------------------------------------------------------------->>


def handle_ask_price(cl, user_id):
    image_path = os.path.join("assets", "price_list.jpg")

    if not os.path.exists(image_path):
        print("[ERROR IMAGE PATH] no image")
        return

    try:
        cl.direct_send_photo(image_path, [user_id])

    except Exception as e:
        print(f"[ASK PRICE EXCEPTION] Error sending photo: {e}")

