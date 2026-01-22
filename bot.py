import os
import disnake
from disnake.ext import commands
from dotenv import load_dotenv

# Загрузка .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("API_KEY")


intents = disnake.Intents.all()
intents.message_content = True

bot = commands.InteractionBot(intents=intents)


COGS = [
    "cogs.context",
    "cogs.memories",  
    "cogs.ai",              
    "cogs.adminCommand",
    "cogs.helpUI"              
]

for cog in COGS:
    try:
        bot.load_extension(cog)
        print(f"Cog {cog} загружен")
    except Exception as e:
        print(f"Ошибка при загрузке {cog}: {e}")


@bot.event
async def on_ready():
    print(f"Бот запущен! Логин: {bot.user}")


# Запуск бота
bot.run(TOKEN)


