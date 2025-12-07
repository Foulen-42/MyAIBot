import os
import re
import aiohttp
import disnake
from disnake.ext import commands

from .memories import MemoriesManager

API_KEY = os.getenv("API_KEY")
DEFAULT_SYSTEM_PROMPT = (
    "Ти розмовляєш українською та допомагаєш користувачу."
    "Якщо користувач запитує свій нік, відповідай коротко, дружелюбно та природно, Не додавай ID."
    "Спогади користувача використовуй при відповіді на відповідні питання."
    "не відповідати любу конструкцію що схожа на [User: Assistant | ID: 0]."
)

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memories = MemoriesManager()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return  # игнорируем сообщения ботов

        ctx_cog = self.bot.get_cog("ContextManager")
        if not ctx_cog:
            return

        user_text = message.content

        # -------------------------
        # Проверка на просьбу "запам'ятай"
        # -------------------------
        pattern = r"^(запам'ятай|remember|запомни)\s+(.+)"
        match = re.match(pattern, message.content, re.IGNORECASE)
        if match:
            text_to_remember = match.group(2).strip()
            self.memories.add_memory(message.author.id, text_to_remember)

        # -------------------------
        # Добавляем сообщение в контекст
        # -------------------------
        ctx_cog.add_message(
            message.channel.id,
            message.author.id,
            message.author.name,
            "user",
            user_text
        )

        # -------------------------
        # Формируем prompt: контекст + спогади
        # -------------------------
        context = ctx_cog.get_context(message.channel.id)
        user_memories = self.memories.get_memories(message.author.id)

        messages = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]
        for msg in context:
            user_info = f"[User: {msg['username']} | ID: {msg['user_id']}]"
            messages.append({"role": msg["role"], "content": f"{user_info} {msg['content']}"})
        for mem in user_memories:
            messages.append({"role": "system", "content": f"Спогад користувача: {mem}"})

        # -------------------------
        # Вызов OpenRouter API
        # -------------------------
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    json={
                        "model": "tngtech/deepseek-r1t2-chimera:free",
                        "messages": messages
                    },
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    }
                ) as resp:

                    raw_text = await resp.text()  # получаем текст, чтобы видеть ошибку целиком
                    
                    # Если ошибка (не 200) — выводим прямо текст ответа сервера
                    if resp.status != 200:
                        ai_answer = f"API Error {resp.status}:\n{raw_text}"
                    else:
                        data = await resp.json()
                        ai_answer = (
                            data.get("choices", [{}])[0]
                            .get("message", {})
                            .get("content", "Помилка API")
                        )

        except Exception as e:
            ai_answer = f"Помилка під час виклику API: {e}"

        # -------------------------
        # Добавляем ответ AI в контекст
        # -------------------------
        ctx_cog.add_message(
            message.channel.id,
            0,
            "Assistant",
            "assistant",
            ai_answer
        )

        await message.channel.send(ai_answer)


def setup(bot):
    bot.add_cog(AI(bot))
