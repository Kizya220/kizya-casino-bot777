import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
import sqlite3
import os

BOT_TOKEN = os.getenv("BOT_TOKEN") or "7793577409:AAHiW1H9nA4Z8A8I-wzSesxJEcwC7tI3eQI"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Ініціалізація БД
def init_db():
    conn = sqlite3.connect("casino.db")
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            language TEXT,
            balance INTEGER DEFAULT 1000
        )
    ''')
    conn.commit()
    conn.close()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "unknown"
    conn = sqlite3.connect("casino.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cur.fetchone()
    if not user:
        lang_kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Українська 🇺🇦"), KeyboardButton(text="Русский 🇷🇺")]
            ],
            resize_keyboard=True
        )
        await message.answer("Оберіть мову / Выберите язык:", reply_markup=lang_kb)
        cur.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
    else:
        await message.answer("Ви вже зареєстровані! / Вы уже зарегистрированы!")

    conn.close()

@dp.message(lambda message: message.text in ["Українська 🇺🇦", "Русский 🇷🇺"])
async def language_set(message: types.Message):
    lang = "ua" if "Українська" in message.text else "ru"
    conn = sqlite3.connect("casino.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET language=? WHERE user_id=?", (lang, message.from_user.id))
    conn.commit()
    conn.close()
    await message.answer("✅ Мову встановлено!" if lang == "ua" else "✅ Язык установлен!")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
