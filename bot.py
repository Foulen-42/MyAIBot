import os
import asyncio
import aiohttp
import datetime
import json
import logging
import disnake
from disnake.ext import commands
from dotenv import load_dotenv

# -----------------------------
# Загрузка .env
# -----------------------------
load_dotenv()
TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("API_KEY")

# -----------------------------
# Интенты
# -----------------------------
intents = disnake.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------------
# Загрузка когов
# -----------------------------
COGS = [
    "cogs.context",  # контекст с автоочисткой
    "cogs.ai"                # AI-ког с обработкой спогадів
]

for cog in COGS:
    try:
        bot.load_extension(cog)
        print(f"Cog {cog} загружен")
    except Exception as e:
        print(f"Ошибка при загрузке {cog}: {e}")

# -----------------------------
# События бота
# -----------------------------
@bot.event
async def on_ready():
    print(f"Бот запущен! Логин: {bot.user}")

# -----------------------------
# Запуск бота
# -----------------------------
bot.run(TOKEN)


