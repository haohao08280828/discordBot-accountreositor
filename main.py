import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

# 儲存帳號資料的字典
accounts = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.slash_command(name="新增帳號")
async def add_account(ctx, 編號: str, 帳號: str, 密碼: str, 收信連結: str, 狀態: str, 價格: float):
    accounts[編號] = {
        "帳號": 帳號,
        "密碼": 密碼,
        "收信連結": 收信連結,
        "狀態": 狀態,
        "價格": 價格
    }
    await ctx.respond(f"帳號 {編號} 已新增")

@bot.slash_command(name="移除帳號")
async def remove_account(ctx):
    options = [discord.SelectOption(label=key, description=f"帳號: {accounts[key]['帳號']}") for key in accounts.keys()]
    
    select = discord.ui.Select(placeholder="選擇要移除的帳號", options=options)
    
    async def select_callback(interaction):
        編號 = select.values[0]
        del accounts[編號]
        await interaction.response.send_message(f"帳號 {編號} 已移除", ephemeral=True)
    
    select.callback = select_callback
    view = discord.ui.View()
    view.add_item(select)
    await ctx.respond("選擇要移除的帳號:", view=view)

@bot.slash_command(name="更新狀態")
async def update_status(ctx):
    options = [discord.SelectOption(label=key, description=f"帳號: {accounts[key]['帳號']}") for key in accounts.keys()]
    
    select = discord.ui.Select(placeholder="選擇要更新的帳號", options=options)
    
    async def select_callback(interaction):
        編號 = select.values[0]
        await interaction.response.send_modal(StatusUpdateModal(編號))
    
    select.callback = select_callback
    view = discord.ui.View()
    view.add_item(select)
    await ctx.respond("選擇要更新的帳號:", view=view)

class StatusUpdateModal(discord.ui.Modal):
    def __init__(self, 編號: str):
        self.編號 = 編號
        super().__init__(title="更新狀態")
        self.add_item(discord.ui.InputText(label="新狀態", placeholder="輸入新的狀態"))

    async def callback(self, interaction: discord.Interaction):
        新狀態 = self.children[0].value
        accounts[self.編號]["狀態"] = 新狀態
        await interaction.response.send_message(f"帳號 {self.編號} 狀態已更新為 {新狀態}", ephemeral=True)

@bot.slash_command(name="看帳號")
async def view_accounts(ctx):
    if not accounts:
        await ctx.respond("目前沒有任何帳號")
    else:
        embed = discord.Embed(title="所有帳號", color=discord.Color.blue())
        for 編號, 資料 in accounts.items():
            account_info = (f"帳號: {資料['帳號']}\n"
                            f"密碼: {資料['密碼']}\n"
                            f"收信連結: {資料['收信連結']}\n"
                            f"狀態: {資料['狀態']}\n"
                            f"價格: {資料['價格']}")
            embed.add_field(name=編號, value=account_info, inline=False)
        await ctx.respond(embed=embed)

@bot.slash_command(name="單獨獲取帳號")
async def get_single_account(ctx):
    options = [discord.SelectOption(label=key, description=f"帳號: {accounts[key]['帳號']}") for key in accounts.keys()]
    
    select = discord.ui.Select(placeholder="選擇要查看的帳號", options=options)
    
    async def select_callback(interaction):
        編號 = select.values[0]
        資料 = accounts[編號]
        account_info = (f"帳號: {資料['帳號']}\n"
                        f"密碼: {資料['密碼']}\n"
                        f"收信連結: {資料['收信連結']}\n"
                        f"狀態: {資料['狀態']}\n"
                        f"價格: {資料['價格']}")
        embed = discord.Embed(title=f"帳號 {編號}", description=account_info, color=discord.Color.green())
        
        button_account = discord.ui.Button(label="輸出帳號", style=discord.ButtonStyle.primary)
        button_password = discord.ui.Button(label="輸出密碼", style=discord.ButtonStyle.primary)
        
        async def button_account_callback(interaction):
            await interaction.response.send_message(f"{資料['帳號']}", ephemeral=True)
        
        async def button_password_callback(interaction):
            await interaction.response.send_message(f"{資料['密碼']}", ephemeral=True)
        
        button_account.callback = button_account_callback
        button_password.callback = button_password_callback
        
        view = discord.ui.View()
        view.add_item(button_account)
        view.add_item(button_password)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    select.callback = select_callback
    view = discord.ui.View()
    view.add_item(select)
    await ctx.respond("選擇要查看的帳號:", view=view)

bot.run(TOKEN)
