import disnake
from disnake.ext import commands

AVAILABLE_MODELS = {
    "deepseek": "tngtech/deepseek-r1t2-chimera:free",
    "amazon nova lite": "amazon/nova-2-lite-v1:free",
    "gpt-oss": "openai/gpt-oss-20b:free",
}

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ctx_cog = self.bot.get_cog("ContextManager")

    @commands.slash_command(
        description="Выбрати канал для бота на цьому сервері",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def set_channel(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel):
        # Проверка уже встроена в default_member_permissions, дополнительная проверка не нужна
        self.ctx_cog.register_channel(inter.guild.id, channel.id)
        await inter.response.send_message(
            f"Бот тепер буде працювати в каналі {channel.mention} на цьому сервері.", ephemeral=True
        )

    @commands.slash_command(
        description="Вибрати модель ШІ для сервера",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def set_model(
        self,
        inter: disnake.ApplicationCommandInteraction,
        model: str = commands.Param(choices=list(AVAILABLE_MODELS.keys()))
    ):
        # Получаем данные сервера
        server_data = self.ctx_cog.load().get(str(inter.guild.id), {})
        if not server_data:
            await inter.response.send_message(
                "Спочатку оберіть канал командою /set_channel.", ephemeral=True
            )
            return

        # Берём первый (или единственный) канал на сервере
        channel_id = list(server_data.keys())[0]

        # Устанавливаем выбранную модель
        selected_model = AVAILABLE_MODELS.get(model, AVAILABLE_MODELS["deepseek"])
        self.ctx_cog.set_model(inter.guild.id, int(channel_id), selected_model)

        await inter.response.send_message(
            f"Модель для цього серверу встановлена на **{model}** ({selected_model}).",
            ephemeral=True
        )

def setup(bot):
    bot.add_cog(AdminCommands(bot))

