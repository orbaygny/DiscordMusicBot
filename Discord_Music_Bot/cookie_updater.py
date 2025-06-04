import subprocess

def update_cookies():
    try:
        subprocess.run([
            "yt-dlp",
            "--cookies-from-browser", "chrome",
            "--cookies", "cookies.txt"
        ], check=True)
        print("✅ Cookie dosyası başarıyla güncellendi.")
    except subprocess.CalledProcessError as e:
        print("❌ Cookie güncelleme başarısız:", e)
