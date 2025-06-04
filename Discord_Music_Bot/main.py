import discord
from discord.ext import commands
# main.py
from commands import music_commands, playlist_commands
from config import TOKEN
from config import bot


@bot.event
async def on_ready():
    print(f"✅ Bot giriş yaptı: {bot.user}")
    await bot.tree.sync()

bot.run(TOKEN)
