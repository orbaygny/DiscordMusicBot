import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

queues = {}
currentList = 'default'

def get_current_list():
    return currentList

def set_current_list(new_list):
    global currentList
    currentList = new_list

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'cookiefile': 'cookies.txt',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

DEFAULT_PLAYLIST = "default"
PLAYLISTS_FILE = "played_status.json"
song_start_times = {}
auto_next_tasks = {}
# music.py ya da botun ana dosyasında

PLAYLISTS_DIR = "playlists"
DEFAULT_PLAYLIST = "default"

song_queue = {}

TOKEN = "TOKEN HERE!"

