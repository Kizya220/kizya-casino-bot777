import asyncio
import random
import sqlite3
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN") or "PASTE_YOUR_BOT_TOKEN_HERE"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

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

def get_balance(user_id):
    conn = sqlite3.connect("casino.db")
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else 0

def update_balance(user_id, delta):
    conn = sqlite3.connect("casino.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (delta, user_id))
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
        await send_menu(message)
    conn.close()

@dp.message(lambda msg: msg.text in ["Українська 🇺🇦", "Русский 🇷🇺"])
async def language_handler(message: types.Message):
    lang = "ua" if "Українська" in message.text else "ru"
    user_id = message.from_user.id
    conn = sqlite3.connect("casino.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET language=? WHERE user_id=?", (lang, user_id))
    conn.commit()
    conn.close()
    await message.answer("✅ Мову встановлено!" if lang == "ua" else "✅ Язык установлен!")
    await send_menu(message)

async def send_menu(message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎰 Слоти"), KeyboardButton(text="🎲 Рулетка")],
            [KeyboardButton(text="🃏 Блекджек"), KeyboardButton(text="💰 Баланс")]
        ],
        resize_keyboard=True
    )
    await message.answer("🎮 Обери гру:", reply_markup=kb)

@dp.message(lambda msg: msg.text == "💰 Баланс")
async def balance_handler(message: types.Message):
    balance = get_balance(message.from_user.id)
    await message.answer(f"💰 Ваш баланс: {balance} фішок")

@dp.message(lambda msg: msg.text == "🎰 Слоти")
async def slots_handler(message: types.Message):
    symbols = ["🍒", "🍋", "🔔", "🍀", "💎"]
    result = [random.choice(symbols) for _ in range(3)]
    msg = " ".join(result)
    if result[0] == result[1] == result[2]:
        win = 200
        update_balance(message.from_user.id, win)
        await message.answer(f"{msg}
🎉 Виграш: +{win} фішок!")
    else:
        loss = -50
        update_balance(message.from_user.id, loss)
        await message.answer(f"{msg}
😢 Програш: -50 фішок")

@dp.message(lambda msg: msg.text == "🎲 Рулетка")
async def roulette_handler(message: types.Message):
    result = random.choice(["🔴 Червоне", "⚫ Чорне", "🟢 Зеро"])
    if result == "🔴 Червоне":
        update_balance(message.from_user.id, 100)
        msg = f"{result} – 🎉 виграш +100"
    elif result == "⚫ Чорне":
        update_balance(message.from_user.id, 50)
        msg = f"{result} – 🎉 виграш +50"
    else:
        update_balance(message.from_user.id, -100)
        msg = f"{result} – 😢 програш -100"
    await message.answer(msg)

@dp.message(lambda msg: msg.text == "🃏 Блекджек")
async def blackjack_handler(message: types.Message):
    cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    player = random.choice(cards) + random.choice(cards)
    dealer = random.choice(cards) + random.choice(cards)
    if player > dealer and player <= 21:
        update_balance(message.from_user.id, 150)
        result = f"🧑 Гравець: {player}
🤖 Дилер: {dealer}
🎉 Виграш +150"
    else:
        update_balance(message.from_user.id, -100)
        result = f"🧑 Гравець: {player}
🤖 Дилер: {dealer}
😢 Програш -100"
    await message.answer(result)

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
