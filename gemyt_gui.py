import customtkinter as ctk
import yt_dlp
import threading
import os
import sys
from PIL import Image
from plyer import notification
from tkinter import filedialog
import requests
import re


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


themes = {
    "Ruby": "#FF3B3B",
    "Emerald": "#2ECC71",
    "Sapphire": "#3498DB",
    "Topaz": "#F1C40F",
    "Amethyst": "#9B59B6"
}

current_color = themes["Ruby"]
download_path = os.getcwd()


icon_images = {
    "Ruby": "ruby.png",
    "Emerald": "emerald.png",
    "Sapphire": "sapphire.png",
    "Topaz": "topaz.png",
    "Amethyst": "amethyst.png"
}


def darker(color, factor=0.8):
    color = color.lstrip("#")
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"


def get_ffmpeg_path():
    return resource_path("ffmpeg.exe")


def notify_done():
    try:
        notification.notify(
            title=f"{theme_menu.get()}YT Downloader",
            message="Téléchargement terminé ✔",
            timeout=5
        )
    except:
        pass


def choose_folder():
    global download_path
    folder = filedialog.askdirectory()
    if folder:
        download_path = folder
        folder_label.configure(text=f"Dossier : {folder}")


def change_theme(choice):
    global current_color
    current_color = themes[choice]

    title.configure(text_color=current_color)
    button.configure(fg_color=current_color, hover_color=darker(current_color))
    folder_button.configure(fg_color=current_color, hover_color=darker(current_color))
    progress.configure(progress_color=current_color)
    status_label.configure(text_color=current_color)

    option.configure(
        fg_color=current_color,
        button_color=darker(current_color),
        button_hover_color=darker(current_color, 0.7)
    )

    theme_menu.configure(
        fg_color=current_color,
        button_color=darker(current_color),
        button_hover_color=darker(current_color, 0.7)
    )

    # image thème
    img = ctk.CTkImage(Image.open(resource_path(icon_images[choice])), size=(24, 24))
    icon_label.configure(image=img)
    icon_label.image = img

    # icône sécurisée
    try:
        icon_path = resource_path(f"{choice.lower()}.ico")
        if os.path.exists(icon_path):
            app.iconbitmap(icon_path)
    except:
        pass

    title.configure(text=f"{choice}YT Downloader")
    app.title(f"{choice}YT Downloader")


def handle_spotify(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers).text

        match = re.search(r'<title>(.*?)</title>', html)
        if match:
            title = match.group(1)
            title = title.replace(" - song and lyrics by", "")
            title = title.replace(" | Spotify", "")
            title = title.strip()
            return f"ytsearch1:{title}"
    except:
        pass

    return url


def download():
    url = entry.get()

    if not url:
        status_label.configure(text="❌ Aucun lien", text_color="red")
        return

    if "spotify.com" in url:
        url = handle_spotify(url)

    status_label.configure(text="Téléchargement...", text_color=current_color)
    progress.set(0)

    def run():
        try:
            mode = option.get()

            def hook(d):
                if d['status'] == 'downloading':
                    try:
                        percent = float(d.get('_percent_str', '0').replace('%','').strip()) / 100
                        progress.set(percent)
                    except:
                        pass

            ydl_opts = {
                'outtmpl': f'{download_path}/%(artist)s - %(title)s.%(ext)s',
                'ffmpeg_location': get_ffmpeg_path(),
                'progress_hooks': [hook],
                'writethumbnail': True,
                'embedmetadata': True,
            }

            if mode == "MP3":
                ydl_opts.update({
                    'format': 'bestaudio',
                    'postprocessors': [
                        {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'},
                        {'key': 'FFmpegMetadata'},
                        {'key': 'EmbedThumbnail'}
                    ]
                })
            else:
                ydl_opts.update({
                    'format': 'bestvideo+bestaudio/best'
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            progress.set(1)
            status_label.configure(text="✔ Terminé", text_color="green")

            notify_done()
            os.startfile(download_path)

        except Exception as e:
            status_label.configure(text=f"Erreur : {e}", text_color="red")

    threading.Thread(target=run).start()


ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.geometry("550x480")


try:
    icon_path = resource_path("ruby.ico")
    if os.path.exists(icon_path):
        app.iconbitmap(icon_path)
except:
    pass

app.title("RubyYT Downloader")


frame_title = ctk.CTkFrame(app, fg_color="transparent")
frame_title.pack(pady=10)

img = ctk.CTkImage(Image.open(resource_path("ruby.png")), size=(24, 24))
icon_label = ctk.CTkLabel(frame_title, image=img, text="")
icon_label.pack(side="left", padx=5)

title = ctk.CTkLabel(frame_title, text="RubyYT Downloader", font=("Arial", 20), text_color=current_color)
title.pack(side="left")


entry = ctk.CTkEntry(app, width=420, placeholder_text="Colle un lien (YouTube, Spotify, etc...)")
entry.pack(pady=10)

platform_label = ctk.CTkLabel(
    app,
    text="YouTube • Spotify • SoundCloud • TikTok • Instagram • Twitter",
    font=("Arial", 11),
    text_color="gray"
)
platform_label.pack(pady=2)

option = ctk.CTkOptionMenu(app, values=["MP3", "MP4"])
option.pack(pady=10)


folder_button = ctk.CTkButton(
    app,
    text="Choisir dossier",
    command=choose_folder,
    fg_color=current_color,
    hover_color=darker(current_color),
    corner_radius=12,
    height=35
)
folder_button.pack(pady=5)

folder_label = ctk.CTkLabel(app, text=f"Dossier : {download_path}")
folder_label.pack()

theme_menu = ctk.CTkOptionMenu(app, values=list(themes.keys()), command=change_theme)
theme_menu.pack(pady=10)
theme_menu.set("Ruby")

button = ctk.CTkButton(
    app,
    text="Télécharger",
    command=download,
    fg_color=current_color,
    hover_color=darker(current_color),
    corner_radius=12,
    height=40
)
button.pack(pady=15)

progress = ctk.CTkProgressBar(app, width=420)
progress.pack(pady=10)
progress.set(0)

status_label = ctk.CTkLabel(app, text="", text_color=current_color)
status_label.pack(pady=10)

app.mainloop()