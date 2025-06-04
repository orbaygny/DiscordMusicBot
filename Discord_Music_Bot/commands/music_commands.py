import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp
import time
import random
import asyncio 
import json
# commands.py
from config import bot, queues,auto_next_tasks,DEFAULT_PLAYLIST,set_current_list
from core.player import (get_song_info,play_next)
@bot.tree.command(name="çal", description="Şarkı çal veya kuyruğa ekle")
@app_commands.describe(arama="YouTube URL'si veya şarkı adı")
async def cal(interaction: discord.Interaction, arama: str):
    await interaction.response.defer()

    voice_channel = interaction.user.voice.channel if interaction.user.voice else None
    if not voice_channel:
        await interaction.followup.send("❌ Önce bir ses kanalına katılmalısın.")
        return

    guild_id = interaction.guild.id
    queues.setdefault(guild_id, [])

    try:
        song_info = await get_song_info(arama)
    except Exception as e:
        await interaction.followup.send(f"❌ Şarkı bulunamadı veya oynatılamıyor.\nHata: {e}")
        return

    queues[guild_id].append(song_info)

    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if not voice_client:
        voice_client = await voice_channel.connect()

    if not voice_client.is_playing():
        await play_next(interaction, guild_id)
        await interaction.followup.send(f"🎶 Şimdi çalıyor: **{song_info['title']}**")
    else:
        await interaction.followup.send(f"✅ Kuyruğa eklendi: **{song_info['title']}**")

@bot.tree.command(name="durdur", description="Çalan şarkıyı durdurur")
async def durdur(interaction: discord.Interaction):
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await interaction.response.send_message("⏸️ Şarkı duraklatıldı.")
    else:
        await interaction.response.send_message("❌ Şu anda çalan bir şarkı yok.")

@bot.tree.command(name="devam", description="Duran şarkıyı devam ettirir")
async def devam(interaction: discord.Interaction):
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await interaction.response.send_message("▶️ Şarkı devam ettirildi.")
    else:
        await interaction.response.send_message("❌ Şu anda duraklatılmış bir şarkı yok.")

@bot.tree.command(name="geç", description="Sonraki şarkıya geç")
async def gec(interaction: discord.Interaction):
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    guild_id = interaction.guild.id

    if voice_client and voice_client.is_playing():
        task = auto_next_tasks.get(guild_id)
        if task and not task.done():
            task.cancel()

        voice_client.stop()
        await interaction.response.send_message("⏭️ Sonraki şarkıya geçiliyor.")
        await play_next(interaction, guild_id)
    else:
        await interaction.response.send_message("❌ Şu anda çalan bir şarkı yok.")

@bot.tree.command(name="ayrıl", description="Bot ses kanalından çıkar")
async def ayril(interaction: discord.Interaction):
    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if voice_client:
        await voice_client.disconnect()
        queues[interaction.guild.id] = []
        # Otomatik geçiş görevini iptal et
        task = auto_next_tasks.get(interaction.guild.id)
        if task and not task.done():
            task.cancel()
        await interaction.response.send_message("👋 Bot kanaldan ayrıldı.")
        set_current_list(DEFAULT_PLAYLIST)
    else:
        await interaction.response.send_message("❌ Bot zaten bir kanalda değil.")