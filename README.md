

---

## Instagram + Telegram Bot 🤖

This bot was created **for practical purposes** for the company **Sanat**, a wellness sanatorium.
It automates user request processing and notifies managers about new inquiries, making communication with clients fast and efficient.

---

## 📝 Functionality

1. **Instagram User Interaction**

> Users send messages to the Instagram bot. The bot uses AI to understand what the user wants and collects the required information.

2. **Database Storage**

> Collected requests are stored in a database (LeadDB) for tracking and processing.

3. **Telegram Notifications for Managers**

> A Telegram bot monitors the database. When a new request appears, it sends a notification to a dedicated chat.
> Managers can **view the request**, **contact the client**, and **update the request status** directly from Telegram.

---

## ⚙️ Installation & Run

1. Clone the repository:

```bash
git clone <repo_url>
```

2. Create a `.env` file with your credentials and tokens:

> Before filling in the `.env` file, you need to:
>
> * Get your **OpenRouter API key** and model name.
> * Create a **Telegram bot via BotFather** to get the token.
> * Prepare your **Instagram username and password**.

Example `.env`:

```env
BOT_TOKEN=<Your Telegram Bot Token>
OPENROUTER_API_KEY=<Your OpenRouter API Key>
OPENROUTER_MODEL=<Your OpenRouter Model Name>
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the bot:

```bash
python main.py
```

> On first run, the bot will ask for login credentials and Telegram chat ID for notifications.
> After that, it starts monitoring Instagram messages, storing requests in the database, and sending Telegram notifications.

---

## 🔧 Tech Stack

* **Python** — core programming language <br>
* **instagrapi** — Instagram API interaction <br>
* **aiogram** — Telegram bot framework <br>
* **OpenAI / OpenRouter** — AI for understanding user intent <br>
* **SQLite / LeadDB** — database for storing requests <br>
* **dotenv** — environment variable management <br>
* **asyncio** — asynchronous background tasks

---

