# playlist.py

import os
import json
from config import PLAYLISTS_FILE,PLAYLISTS_DIR,DEFAULT_PLAYLIST


# Klasör yoksa oluştur
os.makedirs(PLAYLISTS_DIR, exist_ok=True)

def get_playlist_path(name: str) -> str:
    return os.path.join(PLAYLISTS_DIR, f"{name}.json")

def load_playlist(name: str) -> list:
    path = get_playlist_path(name)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return []

        raw_list = json.loads(content)
        # id otomatik atamak için max id bulacağız
        max_id = 0
        new_list = []
        for item in raw_list:
            if isinstance(item, str):
                max_id += 1
                new_list.append({
                    "id": max_id,
                    "url": item,
                    "title": ""
                })
            elif isinstance(item, dict):
                new_list.append(item)
                if "id" in item and isinstance(item["id"], int) and item["id"] > max_id:
                    max_id = item["id"]
            else:
                # Beklenmeyen format varsa atla
                continue
        return new_list



def save_playlist(name: str, songs: list):
    path = get_playlist_path(name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(songs, f, ensure_ascii=False, indent=2)

def create_playlist(name: str) -> bool:
    path = get_playlist_path(name)
    if os.path.exists(path):
        return False  # Zaten var
    save_playlist(name, [])
    return True

def delete_playlist(name: str) -> bool:
    path = get_playlist_path(name)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False

def add_song_to_playlist(name: str, url: str, title: str = ""):
    songs = load_playlist(name)

    # Eğer url zaten varsa, ekleme (id'li ya da url string olarak)
    for song in songs:
        if isinstance(song, dict) and song.get("url") == url:
            return
        elif isinstance(song, str) and song == url:
            return

    # En yüksek id'yi bul
    max_id = 0
    for song in songs:
        if isinstance(song, dict) and isinstance(song.get("id"), int):
            if song["id"] > max_id:
                max_id = song["id"]

    new_song = {
        "id": max_id + 1,
        "url": url,
        "title": title
    }
    songs.append(new_song)
    save_playlist(name, songs)

    # DEFAULT_PLAYLIST senkronizasyonu (eski kod)
    if name != DEFAULT_PLAYLIST:
        add_song_to_playlist(DEFAULT_PLAYLIST, url, title)


def remove_song_from_playlist(name: str, song_id: int):
    songs = load_playlist(name)
    song_to_remove = None
    for song in songs:
        if song.get("id") == song_id:
            song_to_remove = song
            break

    if not song_to_remove:
        return False  # id bulunamadı

    # Şarkıyı listeden çıkar
    updated_songs = [song for song in songs if song.get("id") != song_id]
    save_playlist(name, updated_songs)

    # Eğer default listesi değilse, aynı URL'yi default listesinden sil
    if name != DEFAULT_PLAYLIST:
        remove_song_from_playlist_by_url(DEFAULT_PLAYLIST, song_to_remove["url"])

    return True


def remove_song_from_playlist_by_url(name: str, url: str):
    songs = load_playlist(name)
    updated_songs = [song for song in songs if song.get("url") != url]
    save_playlist(name, updated_songs)



def list_playlists() -> list:
    return [f[:-5] for f in os.listdir(PLAYLISTS_DIR) if f.endswith(".json")]

def list_songs(name: str) -> list:
    songs = load_playlist(name)
    return [s['url'] if isinstance(s, dict) else s for s in songs]

def list_songs_byname(name: str) -> list:
    # Tüm şarkı sözlüklerini döndürür (id, url, title)
    return load_playlist(name)

def load_played_status():
    try:
        with open(PLAYLISTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_played_status(data):
    with open(PLAYLISTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)