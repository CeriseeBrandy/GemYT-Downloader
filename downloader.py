import yt_dlp
import os
import requests
import re


def clean_url(url):
    if "&index=" in url:
        url = url.split("&index=")[0]
    return url


def handle_spotify(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers).text

        match = re.search(r'<title>(.*?)</title>', html)
        title = ""
        if match:
            title = match.group(1)
            title = title.replace(" - song and lyrics by", "")
            title = title.replace(" | Spotify", "")
            title = title.strip()

        img_match = re.search(r'<meta property="og:image" content="(.*?)"', html)
        image_url = img_match.group(1) if img_match else None

        return {
            "search": f"ytsearch1:{title}",
            "title": title,
            "thumbnail": image_url
        }

    except:
        return {"search": url, "title": None, "thumbnail": None}


def get_video_info(url):
    try:
        url = clean_url(url)

        spotify_data = None

        if "spotify.com" in url:
            spotify_data = handle_spotify(url)
            url = spotify_data["search"]

        ydl_opts = {
            'quiet': True,
            'noplaylist': True,
            'skip_download': True,
            'extract_flat': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if spotify_data:
            if spotify_data["title"]:
                info["title"] = spotify_data["title"]
            if spotify_data["thumbnail"]:
                info["thumbnail"] = spotify_data["thumbnail"]

        return info

    except Exception as e:
        print("❌ Erreur get_video_info :", e)
        return {"title": "Erreur", "thumbnail": None}


def download_video(url, download_path, mode, quality, progress_callback=None, playlist=False):

    url = clean_url(url)

    if "spotify.com" in url:
        url = handle_spotify(url)["search"]

    def hook(d):
        if d['status'] == 'downloading':
            try:
                percent = d.get('_percent_str', '0').replace('%', '').strip()
                percent = float(percent) / 100
                if progress_callback:
                    progress_callback(percent)
            except:
                pass

        elif d['status'] == 'finished':
            if progress_callback:
                progress_callback(1)

    if quality == "1080p":
        format_sel = "bestvideo[height<=1080]+bestaudio/best"
    elif quality == "720p":
        format_sel = "bestvideo[height<=720]+bestaudio/best"
    else:
        format_sel = "bestvideo+bestaudio/best"

    ydl_opts = {
        'outtmpl': f'{download_path}/%(playlist_title)s/%(title)s.%(ext)s' if playlist else f'{download_path}/%(artist)s - %(title)s.%(ext)s',
        'ffmpeg_location': os.path.join(os.getcwd(), "ffmpeg.exe"),
        'progress_hooks': [hook],
        'writethumbnail': True,
        'embedmetadata': True,
        'noplaylist': not playlist,
        'format': format_sel
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

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as e:
        print("❌ Erreur download :", e)
        if progress_callback:
            progress_callback(0)