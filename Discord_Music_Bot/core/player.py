import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp
import time
import random
import asyncio 
import json
# music.py
from config import YDL_OPTIONS, FFMPEG_OPTIONS, queues, bot,song_start_times,auto_next_tasks,get_current_list
from .playlist import ( list_songs, load_played_status, save_played_status)

async def add_to_queue(guild_id: int, song_info: dict, text_channel: discord.TextChannel = None):
    queues.setdefault(guild_id, [])
    try:
        queues[guild_id].append(song_info)
        return True
    except Exception as e:
        if text_channel:
            await text_channel.send(f"❌ Şarkı kuyruğa eklenemedi: {e}")
        return False


async def get_song_info(query: str) -> dict:
    def _extract():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            return ydl.extract_info(query, download=False)

    info = await asyncio.to_thread(_extract)
    if 'entries' in info:
        return info['entries'][0]
    return info

        
async def auto_advance_after(guild_id: int, interaction: discord.Interaction, duration: int):
    try:
        await asyncio.sleep(duration)
        await play_next(interaction, guild_id)
    except asyncio.CancelledError:
        print(f"Auto advance task iptal edildi: guild_id={guild_id}")

async def play_next(interaction: discord.Interaction, guild_id: int):
    queue = queues.get(guild_id, [])
    if not queue:
        # Kuyruk boşsa, default listeden rastgele çal
        success = await play_random_from_list(interaction)
        if not success:
            voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
            if voice_client and voice_client.is_connected():
                await voice_client.disconnect()
        return

    # Mevcut play_next kodun burada devam eder...
    song = queue.pop(0)

    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if not voice_client or not voice_client.is_connected():
        return

    source = await discord.FFmpegOpusAudio.from_probe(song['url'], **FFMPEG_OPTIONS)

    start_time = time.time()
    song_duration = song.get('duration', 0)
    song_start_times[guild_id] = (start_time, song_duration)

    voice_client.play(source)

    task = auto_next_tasks.get(guild_id)
    if task and not task.done():
        task.cancel()
    auto_next_tasks[guild_id] = bot.loop.create_task(auto_advance_after(guild_id, interaction, song_duration))

    async def send_now_playing():
        await interaction.channel.send(f"🎶 Şimdi çalıyor: **{song['title']}**")
    bot.loop.create_task(send_now_playing())

async def queue_song(guild: discord.Guild, url: str, title: str, channel: discord.TextChannel):
    guild_id = guild.id
    queues.setdefault(guild_id, [])

    try:
        song_info = await get_song_info(url)
        queues[guild_id].append(song_info)
    except Exception as e:
        await channel.send(f"❌ Şarkı kuyruğa eklenemedi: {e}")

async def play_random_from_list(interaction: discord.Interaction):
    _current = get_current_list()
    songs = list_songs(_current)  # Bu fonksiyon sadece URL listesi döndürüyor, senin kodunda var zaten
    if not songs:
        # Default liste boşsa ya da yoksa
        await interaction.channel.send("⚠️ Default liste boş, rastgele şarkı çalınamıyor.")
        return False

    try:
        # get_next_song fonksiyonu JSON'daki durumu da yönetiyor
        url = get_next_song(_current, songs)
        song_info = await get_song_info(url)
    except Exception as e:
        await interaction.channel.send(f"❌ Listedeki şarkı oynatılamadı: {e}")
        return False

    guild_id = interaction.guild.id
    queues.setdefault(guild_id, [])
    queues[guild_id].append(song_info)

    voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if not voice_client or not voice_client.is_connected():
        voice_channel = interaction.user.voice.channel if interaction.user.voice else None
        if not voice_channel:
            await interaction.channel.send("❌ Önce bir ses kanalına katılmalısın.")
            return False
        voice_client = await voice_channel.connect()

    if not voice_client.is_playing():
        await play_next(interaction, guild_id)

    await interaction.channel.send(f"Listeden rastgele şarkı çalınıyor: **{song_info['title']}**")
    return True

def get_next_song(list_name, all_songs):
    data = load_played_status()

    # Liste json içinde yoksa oluştur
    if list_name not in data:
        data[list_name] = {
            "played": [],
            "not_played": all_songs.copy()
        }
    else:
        played = set(data[list_name]["played"])
        not_played = set(data[list_name]["not_played"])

        # Yeni eklenmiş şarkıları tespit et
        current_songs = set(all_songs)
        new_songs = current_songs - played - not_played

        # Yeni şarkıları not_played listesine ekle
        data[list_name]["not_played"] = list(set(data[list_name]["not_played"]).union(new_songs))

    played = data[list_name]["played"]
    not_played = data[list_name]["not_played"]

    # Eğer çalınmamış şarkı kalmadıysa sıfırla
    if not not_played:
        not_played = all_songs.copy()
        played = []

    # Rastgele şarkı seç
    next_song = random.choice(not_played)
    not_played.remove(next_song)
    played.append(next_song)

    # Değişiklikleri kaydet
    data[list_name]["played"] = played
    data[list_name]["not_played"] = not_played
    save_played_status(data)

    return next_song