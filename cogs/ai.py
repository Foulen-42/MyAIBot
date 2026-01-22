import os
import re
import aiohttp
import disnake
from disnake.ext import commands
from datetime import datetime

API_KEY = os.getenv("API_KEY")
DEFAULT_SYSTEM_PROMPT = (
    "Ти допомагаєш користувачу, мову можна змінювати за бажанням користувача."
    "Не потрібно завжди привітватися, якщо в історії є попередні повідомлення із роллю assistant."
    "Якщо користувач запитує свій нік, відповідай коротко, дружелюбно та природно, не додавай ID."
    "Нік користувача показуй обертаючи його у два ` з обох боків."
    "Спогади користувача використовуй лише за потреби."
    "У відповіді максимум 1800 символів."

)

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.memories = self.bot.get_cog("MemoriesManager")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return  # ігноруємо ботов та ПП

        ctx_cog = self.bot.get_cog("ContextManager")
        if not ctx_cog:
            return

        server_id = message.guild.id
        server_data = ctx_cog.load().get(str(server_id))
        if not server_data:
            return  # сервер не зареєстрований адміном

        # беремо перший зареєстрований канал
        channel_id = int(list(server_data.keys())[0])
        if message.channel.id != channel_id:
            return  # ігноруємо всі інші канали

        user_text = message.content

        # первірка на прохання "запам'ятай"
        pattern = r"^(запам'ятай|remember|запомни|запамятай).(.+)"
        match = re.match(pattern, user_text, re.IGNORECASE)
        if match:
            text_to_remember = match.group(2).strip()
            self.memories.add_memory(message.author.id, text_to_remember)


        # Додаємо повідомлення у контекст
        ctx_cog.add_message(server_id, channel_id, message.author.id, message.author.name, "user", user_text)


        # Формуємо prompt: контекст + спогади
        context = ctx_cog.get_context(server_id, channel_id)
        user_memories = self.memories.get_memories(message.author.id)
        
        messages = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]
        for msg in context:
            if msg["role"] == "user":
                messages.append({
                "role": "user",
                "content": f"<uid:{msg['user_id']}> {msg['username']}: {msg['content']}"
            })
            else:
                messages.append({
                    "role": "assistant",
                    "content": msg["content"]
                })

        for mem in user_memories:
            messages.append({"role": "system", "content": f"Спогад користувача: {mem}"})

        # Отримуємо ШІ-модель сервера
        model_name = ctx_cog.get_model(server_id, channel_id) or "tngtech/deepseek-r1t2-chimera:free"

        # Виклик OpenRouter API з typing
        async with message.channel.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        json={"model": model_name, "messages": messages},
                        headers={
                            "Authorization": f"Bearer {API_KEY}",
                            "Content-Type": "application/json"
                        }
                    ) as resp:
                        raw_text = await resp.text()
                        if resp.status != 200:
                            # лог у консоль
                            print("=== OPENROUTER API ERROR ===")
                            print(raw_text)
                            print("============================")

                            # коротке повідомлення користувачу
                            time_str = datetime.now().strftime("%H:%M:%S")
                            ai_answer = f"⚠️ Помилка API ({resp.status}) о {time_str}"
                        else:
                            data = await resp.json()
                            ai_answer = (
                            data.get("choices", [{}])[0]
                            .get("message", {})
                            .get("content", "Помилка API")
                            )
            except Exception as e:
                ai_answer = f"Помилка під час виклику API: {e}"

        # Додаємо відповідь ШІ у контекст
        ctx_cog.add_message(server_id, channel_id, None, None, "assistant", ai_answer)

        await message.channel.send(ai_answer)

def setup(bot):
    bot.add_cog(AI(bot))
