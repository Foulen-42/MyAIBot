import disnake
from disnake.ext import commands

class HelpUI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Головне вікно
    def get_main_embed_and_select(self):
        embed = disnake.Embed(title="Доступні команди",description="Виберіть розділ команд нижче:",color=disnake.Color.blurple())
        embed.add_field(name="Модерація", value="/mute, /unmute, /ban, /unban, /clear", inline=False)
        embed.add_field(name="Налаштування", value="/set_channel, /set_model, /clear_history", inline=False)

        options = [
            disnake.SelectOption(label="Модерація", description="Команди для модерації", value="moderation"),
            disnake.SelectOption(label="Налаштування", description="Команди для налаштування бота", value="settings"),
        ]
        select = disnake.ui.Select(placeholder="Обрати розділ", options=options)
        return embed, select

    # Команда /help
    @commands.slash_command(description="Показати список команд")
    async def help(self, inter: disnake.ApplicationCommandInteraction):
        embed, select = self.get_main_embed_and_select()
        view = disnake.ui.View()

        async def select_callback(inter_select: disnake.MessageInteraction):
            if select.values[0] == "moderation":
                await inter_select.response.edit_message(embed=self.get_moderation_embed(), view=self.get_back_view())
            elif select.values[0] == "settings":
                await inter_select.response.edit_message(embed=self.get_settings_embed(), view=self.get_back_view())

        select.callback = select_callback
        view.add_item(select)

        await inter.response.send_message(embed=embed, view=view, ephemeral=True)

    # Embed для Модерації
    def get_moderation_embed(self):
        return disnake.Embed(
            title="Разділ: Модерація",
            description=(
                "``/mute <користувач|ID> <час> [причина]`` - Зам'ютити користувача\n"
                "``/unmute <користувач|ID>`` - Розм'ютити користувача\n"
                "``/ban <користувач|ID> [причина]`` - Забанити користувача\n"
                "``/unban <користувач|ID>`` - Розбанити користувача\n"
                "``/clear <кількість повідомлень>`` - Очистити повідомлення"
            ),
            color=disnake.Color.red()
        )

    # Embed для Налаштувань
    def get_settings_embed(self):
        return disnake.Embed(
            title="Разділ: Налаштування",
            description=(
                "``/set_channel <канал>`` - Вибрати канал для бота\n"
                "``/set_model <модель>`` - Вибрати модель ШІ для сервера\n"
                "``/clear_history`` - Очистити історію повідомлень ШІ на сервері"
            ),
            color=disnake.Color.green()
        )

    # Кнопка "Назад"
    def get_back_view(self):
        embed, select = self.get_main_embed_and_select()
        view = disnake.ui.View()

        button = disnake.ui.Button(label="Назад", style=disnake.ButtonStyle.secondary)

        async def back_callback(inter_btn: disnake.MessageInteraction):
            view_new = disnake.ui.View()
            async def select_callback(inter_select: disnake.MessageInteraction):
                if select.values[0] == "moderation":
                    await inter_select.response.edit_message(embed=self.get_moderation_embed(), view=self.get_back_view())
                elif select.values[0] == "settings":
                    await inter_select.response.edit_message(embed=self.get_settings_embed(), view=self.get_back_view())

            select.callback = select_callback
            view_new.add_item(select)
            await inter_btn.response.edit_message(embed=embed, view=view_new)

        button.callback = back_callback
        view.add_item(button)
        return view

def setup(bot):
    bot.add_cog(HelpUI(bot))