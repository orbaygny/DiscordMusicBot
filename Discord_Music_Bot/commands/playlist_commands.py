import discord
from discord.ext import commands
from discord import app_commands
# commands.py
from config import bot, tree, currentList,DEFAULT_PLAYLIST,get_current_list,set_current_list
from core.player import (get_song_info,play_random_from_list)
from core.playlist import(create_playlist,delete_playlist,add_song_to_playlist,remove_song_from_playlist,list_playlists,list_songs_byname)

@tree.command(name="liste_ekle", description="Yeni bir oynatma listesi oluştur")
@app_commands.describe(liste_adi="Oluşturulacak liste adı")
async def liste_ekle(interaction: discord.Interaction, liste_adi: str):
    if create_playlist(liste_adi):
        await interaction.response.send_message(f"✅ `{liste_adi}` adlı liste oluşturuldu.")
    else:
        await interaction.response.send_message(f"❌ `{liste_adi}` adlı liste zaten var.")

@tree.command(name="liste_sil", description="Bir oynatma listesini sil")
@app_commands.describe(liste_adi="Silinecek liste adı")
async def liste_sil(interaction: discord.Interaction, liste_adi: str):
    if delete_playlist(liste_adi):
        await interaction.response.send_message(f"🗑 `{liste_adi}` listesi silindi.")
    else:
        await interaction.response.send_message(f"❌ `{liste_adi}` listesi bulunamadı.")

@tree.command(name="listeye_sarki_ekle", description="Bir listeye şarkı URL'si ekle")
@app_commands.describe(liste_adi="Hedef liste adı", url="Eklenecek şarkı URL'si")
async def listeye_sarki_ekle(interaction: discord.Interaction, liste_adi: str, url: str):
    await interaction.response.defer()  # İlk olarak ertele

    try:
        song_info = await get_song_info(url)
        add_song_to_playlist(liste_adi, url, song_info.get("title", ""))
        await interaction.followup.send(f"✅ Şarkı `{liste_adi}` listesine eklendi.")
    except Exception as e:
        await interaction.followup.send(f"❌ Şarkı eklenirken hata: {e}")


@tree.command(name="listeden_sarki_sil", description="Bir listeden şarkı sil")
@app_commands.describe(liste_adi="Hedef liste adı", id="Silinecek şarkının id'si")
async def listeden_sarki_sil(interaction: discord.Interaction, liste_adi: str, id: int):
    success = remove_song_from_playlist(liste_adi, id)
    if success:
        await interaction.response.send_message(f"🗑 Şarkı (ID: {id}) `{liste_adi}` listesinden silindi.")
    else:
        await interaction.response.send_message(f"❌ `{liste_adi}` listesinde ID {id} bulunamadı.")



@tree.command(name="listeleri_goster", description="Tüm liste adlarını göster")
async def listeleri_goster(interaction: discord.Interaction):
    playlists = list_playlists()
    if not playlists:
        await interaction.response.send_message("📭 Henüz hiç liste yok.")
    else:
        await interaction.response.send_message("📚 Mevcut listeler:\n" + "\n".join(f"- {p}" for p in playlists))

@tree.command(name="listeyi_goster", description="Bir listedeki tüm şarkıları göster")
@app_commands.describe(liste_adi="Listesi gösterilecek liste adı")
async def listeyi_goster(interaction: discord.Interaction, liste_adi: str):
    songs = list_songs_byname(liste_adi)
    if not songs:
        await interaction.response.send_message(f"📭 `{liste_adi}` listesi boş veya yok.")
    else:
        msg = "\n".join(f"{song['id']}. {song['title']}" for song in songs)
        await interaction.response.send_message(f"🎵 `{liste_adi}` listesindeki şarkılar:\n{msg[:1900]}")

@bot.tree.command(name="listeyi_cal", description="Bir listedeki şarkıları teker teker kuyruğa ekler ve çalar.")
@app_commands.describe(liste_adi="Çalmak istediğiniz oynatma listesinin adı")
async def listeyi_cal(interaction: discord.Interaction, liste_adi: str):
    set_current_list(liste_adi)
    await interaction.response.defer()  # Yanıt süresi sınırlıysa, botu bekletmeden önce yanıtla
    success = await play_random_from_list(interaction)
    if not success:
        await interaction.followup.send("⚠️ Şarkı çalınamadı, liste boş olabilir veya hata oluştu.")


@tree.command(name="listeyi_calmayi_durdur", description="Çalan listeyi durdurur")
async def liste_durdur(interaction: discord.Interaction):
  set_current_list(DEFAULT_PLAYLIST)
  await interaction.response.send_message("❌ Liste artık çalınmıyor")