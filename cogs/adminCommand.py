import disnake
from disnake.ext import commands, tasks
import datetime

AVAILABLE_MODELS = {
    "deepseek": "tngtech/deepseek-r1t2-chimera:free",
    "nvidia-nemotron": "nvidia/nemotron-3-nano-30b-a3b:free"
}

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ctx_cog = self.bot.get_cog("ContextManager")

    @commands.slash_command(description="Выбрати канал для бота на цьому сервері",default_member_permissions=disnake.Permissions(administrator=True))
    async def set_channel(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel):
        self.ctx_cog.register_channel(inter.guild.id, channel.id)
        await inter.response.send_message(
            f"Бот тепер буде працювати в каналі {channel.mention} на цьому сервері.", ephemeral=True
        )

    @commands.slash_command(description="Вибрати модель ШІ для сервера",default_member_permissions=disnake.Permissions(administrator=True))
    async def set_model(self,inter: disnake.ApplicationCommandInteraction,model: str = commands.Param(choices=list(AVAILABLE_MODELS.keys()))):
        # Отримуємо дані сервера
        server_data = self.ctx_cog.load().get(str(inter.guild.id), {})
        if not server_data:
            await inter.response.send_message(
                "Спочатку оберіть канал командою /set_channel.", ephemeral=True
            )
            return

        # Отримуємо перший (або єдиний) канал на сервері
        channel_id = list(server_data.keys())[0]

        # Встановлюємо обрану модель
        selected_model = AVAILABLE_MODELS.get(model, AVAILABLE_MODELS["deepseek"])
        self.ctx_cog.set_model(inter.guild.id, int(channel_id), selected_model)

        await inter.response.send_message(
            f"Модель для цього серверу встановлена на **{model}** ({selected_model}).",
            ephemeral=True
        )

    @commands.slash_command(description="Очистити історію повідомлення у ШІ",default_member_permissions=disnake.Permissions(administrator=True))
    async def clear_history(self, inter: disnake.ApplicationCommandInteraction):
        self.ctx_cog.clear_history(inter.guild.id)
        await inter.response.send_message("Історія повідомлень очищена.", ephemeral=True)


    @commands.slash_command(description="Зам'ютити користувача на деякий час у хвилинах",default_member_permissions=disnake.Permissions(administrator=True))
    async def mute(self,interaction: disnake.ApplicationCommandInteraction,member: disnake.Member,time: int,reason: str = "Без причини"):
        time_dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=time)

        await member.timeout(until=time_dt, reason=reason)

        await interaction.response.send_message(
            f"{member.mention} зам'ютений на {time} хв.\nПричина: {reason}",
            ephemeral=True
        )

    @commands.slash_command(description="Розм'ютити користувача", default_member_permissions=disnake.Permissions(administrator=True))
    async def unmute(self,interaction: disnake.ApplicationCommandInteraction,member: str,):
        await member.timeout(reason=None, until=None)
        await interaction.response.send_message(f"{member.mention} розм'ютений.", ephemeral=True)

    @commands.slash_command(description="Забанити користувача",default_member_permissions=disnake.Permissions(administrator=True))
    async def ban(self, interaction, user: str, *, reason: str = None):
        if user.isdigit():
            user = await interaction.guild.fetch_member(int(user))
        else:
            try:
                user = await commands.MemberConverter().convert(interaction, user)
            except:
                await interaction.response.send_message("Користувача не знайдено!", ephemeral=True)
                return

        await interaction.guild.ban(user, reason=reason)
        await interaction.response.send_message(f"{user.mention} забанений за {reason}.", ephemeral=True)

    @commands.slash_command(
        description="Розбанити користувача",
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def unban(self, interaction, user: str):
        bans_list = [ban async for ban in interaction.guild.bans()]
        target = None

        if user.isdigit():
            user_id = int(user)
            for ban_entry in bans_list:
                if ban_entry.user.id == user_id:
                    target = ban_entry.user
                    break
        else:
            for ban_entry in bans_list:
                if str(ban_entry.user) == user:
                    target = ban_entry.user
                    break

        if target is None:
            await interaction.response.send_message("Користувача не знайдено в бан-листі!", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.ban_members:
            await interaction.response.send_message("У мене немає прав для розбану!", ephemeral=True)
            return

        await interaction.guild.unban(target)
        await interaction.response.send_message(f"{target} розбанений.", ephemeral=True)

    @commands.slash_command(description="Очистити повідомлення", default_member_permissions=disnake.Permissions(administrator=True))
    async def clear(self, interaction, amount: int):
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"Очищено {amount} повідомлень.", ephemeral=True)

def setup(bot):
    bot.add_cog(AdminCommands(bot))

