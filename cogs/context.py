import json
import os
import datetime
import asyncio
from disnake.ext import commands

class ContextManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = "context.json"
        self.timeout_minutes = 15  # сколько минут бездействия до закрытия окна
        self.max_messages = 20     # длина контекста

        # создать файл если нет
        if not os.path.exists(self.file):
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4)

        # запускаем фоновую задачу очистки
        bot.loop.create_task(self.session_cleanup_loop())

    # -----------------------------
    # JSON helpers
    # -----------------------------
    def load(self):
        with open(self.file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # -----------------------------
    #  Добавление сообщений в контекст
    # -----------------------------
    def add_message(self, channel_id: int, user_id: int, username: str, role: str, content: str):
        """
        role: "user" | "assistant"
        """

        data = self.load()
        cid = str(channel_id)

        if cid not in data:
            data[cid] = {
                "messages": [],
                "last_activity": datetime.datetime.utcnow().isoformat()
            }

        data[cid]["messages"].append({
            "user_id": user_id,
            "username": username,
            "role": role,
            "content": content
        })

        # ограничение размера контекста
        if len(data[cid]["messages"]) > self.max_messages:
            data[cid]["messages"] = data[cid]["messages"][-self.max_messages:]

        # обновляем время активности
        data[cid]["last_activity"] = datetime.datetime.utcnow().isoformat()

        self.save(data)

    # -----------------------------
    # Получение контекста канала
    # -----------------------------
    def get_context(self, channel_id: int):
        data = self.load()
        return data.get(str(channel_id), {}).get("messages", [])

    # -----------------------------
    # Очистка контекста вручную
    # -----------------------------
    def clear_context(self, channel_id: int):
        data = self.load()
        cid = str(channel_id)
        if cid in data:
            del data[cid]
            self.save(data)

    # -----------------------------
    # Автоматическое закрытие сессий
    # -----------------------------
    async def session_cleanup_loop(self):
        """
        Фоновая задача:
        удаляет контекст канала, если нет активности N минут.
        """
        while True:
            await asyncio.sleep(60)  # проверяем каждую минуту

            data = self.load()
            now = datetime.datetime.utcnow()

            remove_list = []

            for cid, info in data.items():
                try:
                    last = datetime.datetime.fromisoformat(info["last_activity"])
                except:
                    continue

                delta = now - last
                if delta.total_seconds() > self.timeout_minutes * 60:
                    remove_list.append(cid)

            # удаляем просроченные
            if remove_list:
                for cid in remove_list:
                    del data[cid]
                self.save(data)

def setup(bot):
    bot.add_cog(ContextManager(bot))
