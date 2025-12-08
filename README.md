Instagram + Telegram Bot with AI and Database Integration
Project Overview

This bot was created for practical purposes for the company Sanat, which is a wellness sanatorium.
Its main goal is to automate user request processing and provide managers with notifications about new inquiries.

Functionality

User interaction via Instagram:
The user sends a message to the Instagram bot, and the bot gathers the necessary information from the user using AI.

Database storage:
The bot stores the collected information as a new entry in the database (LeadDB).

Telegram notifications for managers:
A Telegram bot monitors the database for new requests.
When a new request appears, it sends a message to a dedicated chat where the manager can view the request and contact the client directly if needed.

Installation and Setup

Clone the repository:

git clone <repo_url>


Set up the .env file

Before running the bot, you need to fill in the .env file with the following data:

OpenRouter API key and model name:

Sign up at OpenRouter

and get your API key.

Choose the model you want to use (e.g., GPT-based) and copy its name.

Telegram bot token:

Create a bot via BotFather

on Telegram.

Copy the generated token.

Instagram credentials:
Enter your Instagram username and password for the bot to read user messages.


Install dependencies:

pip install -r requirements.txt


Run the bot:

python main.py


On the first run, the bot will prompt you for login credentials and the chat ID for Telegram notifications.

After that, the bot will start monitoring Instagram messages, store user requests in the database, and send notifications to the Telegram chat.

Tech Stack

Python — main programming language
instagrapi — for interacting with Instagram and reading user messages
aiogram — for building the Telegram bot
OpenAI / OpenRouter AI models — to understand user intent and generate responses
SQLite / LeadDB — database for storing user requests
dotenv — for storing secret keys and tokens
asyncio — for asynchronous message handling and background tasks


