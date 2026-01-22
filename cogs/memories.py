import json
import os
from disnake.ext import commands

class MemoriesManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.folder = "data"
        os.makedirs(self.folder, exist_ok=True)

        self.file = os.path.join(self.folder, "memories.json")
        self.max_length = 200

        if not os.path.exists(self.file):
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4)

    def load(self):
        with open(self.file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_memory(self, user_id: int, text: str):
        text = text[:self.max_length]
        data = self.load()
        uid = str(user_id)
        if uid not in data:
            data[uid] = []
        data[uid].append(text)
        self.save(data)

    def get_memories(self, user_id: int):
        data = self.load()
        return data.get(str(user_id), [])

    def delete_memories(self, user_id: int):
        data = self.load()
        uid = str(user_id)
        if uid in data:
            del data[uid]
            self.save(data)

def setup(bot):
    bot.add_cog(MemoriesManager(bot))