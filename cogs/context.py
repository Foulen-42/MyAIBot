import json
import os
import datetime
import asyncio
from disnake.ext import commands

class ContextManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # -------------------------------
        # Папка и путь как ты хочешь
        # -------------------------------
        self.folder = "data"
        self.file = os.path.join(self.folder, "context.json")

        os.makedirs(self.folder, exist_ok=True)

        # если файла нет — создаём
        if not os.path.exists(self.file):
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4)

        self.timeout_minutes = 1 # РАДИ ТЕСТА
        self.max_messages = 20

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
    # Регистрация сервера/канала
    # -----------------------------
    def register_channel(self, server_id: int, channel_id: int, model: str = "tngtech/deepseek-r1t2-chimera:free"):
        data = self.load()
        sid = str(server_id)
        cid = str(channel_id)

        if sid not in data:
            data[sid] = {}

        
        data[sid][cid] = {
                "model": model,
                "messages": [],
                "last_activity": datetime.datetime.utcnow().isoformat()
        }

        for old_cid in list(data[sid].keys()):
            if old_cid != cid:
                del data[sid][old_cid]


        self.save(data)

    # -----------------------------
    # Добавление сообщений
    # -----------------------------
    def add_message(self, server_id: int, channel_id: int, user_id: int, username: str, role: str, content: str):
        data = self.load()
        sid = str(server_id)
        cid = str(channel_id)

        if sid not in data or cid not in data[sid]:
            return  # сервер/канал не зарегистрирован

        data[sid][cid]["messages"].append({
            "user_id": user_id,
            "username": username,
            "role": role,
            "content": content
        })

        if len(data[sid][cid]["messages"]) > self.max_messages:
            data[sid][cid]["messages"] = data[sid][cid]["messages"][-self.max_messages:]

        data[sid][cid]["last_activity"] = datetime.datetime.utcnow().isoformat()
        self.save(data)

    # -----------------------------
    # Получение контекста
    # -----------------------------
    def get_context(self, server_id: int, channel_id: int):
        data = self.load()
        return data.get(str(server_id), {}).get(str(channel_id), {}).get("messages", [])

    # -----------------------------
    # Получить/установить модель
    # -----------------------------
    def get_model(self, server_id: int, channel_id: int):
        data = self.load()
        return data.get(str(server_id), {}).get(str(channel_id), {}).get("model")

    def set_model(self, server_id: int, channel_id: int, model: str):
        data = self.load()
        sid = str(server_id)
        cid = str(channel_id)

        if sid in data and cid in data[sid]:
            data[sid][cid]["model"] = model
            self.save(data)

    # -----------------------------
    # Авто-очистка старых сессий
    # -----------------------------
    async def session_cleanup_loop(self):
        while True:
            await asyncio.sleep(60)
            data = self.load()
            now = datetime.datetime.utcnow()
            changes = False

            for sid in list(data.keys()):
                for cid in list(data[sid].keys()):
                    try:
                        last = datetime.datetime.fromisoformat(data[sid][cid]["last_activity"])
                    except:
                        continue

                    if (now - last).total_seconds() > self.timeout_minutes * 60:
                        data[sid][cid]["messages"] = []
                        data[sid][cid]["last_activity"] = ""
                        changes = True

                if sid in data and len(data[sid]) == 0:
                    del data[sid]
                    changes = True

            if changes:
                self.save(data)

def setup(bot):
    bot.add_cog(ContextManager(bot))
