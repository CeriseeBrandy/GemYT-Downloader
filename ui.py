import customtkinter as ctk
import threading
import os
from tkinter import filedialog
from PIL import Image
from downloader import download_video, get_video_info
from utils import load_data, save_data


themes = {
    "Ruby": "#FF3B3B",
    "Emerald": "#2ECC71",
    "Sapphire": "#3498DB",
    "Topaz": "#F1C40F",
    "Amethyst": "#9B59B6"
}

icon_images = {
    "Ruby": "assets/ruby.png",
    "Emerald": "assets/emerald.png",
    "Sapphire": "assets/sapphire.png",
    "Topaz": "assets/topaz.png",
    "Amethyst": "assets/amethyst.png"
}


def darker(color, factor=0.8):
    color = color.lstrip("#")
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    return f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.geometry("1050x550")
        self.resizable(False, False)

        self.data = load_data()

        self.current_color = themes["Ruby"]
        self.preview_after_id = None
        self.quality = self.data["settings"].get("quality", "Best")
        self.settings_visible = False

        self.download_path = self.data["settings"].get("download_path", os.getcwd())
        theme = self.data["settings"].get("theme", "Ruby")

        self.title("RubyYT Downloader")

        # ICON INIT
        try:
            self.iconbitmap("assets/ruby.ico")
        except:
            pass

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # ===== SETTINGS =====
        self.settings_frame = ctk.CTkFrame(self.main_container, width=250)

        ctk.CTkLabel(self.settings_frame, text="Settings", font=("Arial", 16, "bold")).pack(pady=10)

        # QUALITY
        ctk.CTkLabel(self.settings_frame, text="Quality").pack(pady=5)
        self.quality_menu = ctk.CTkOptionMenu(
            self.settings_frame,
            values=["Best", "1080p", "720p"],
            command=self.set_quality
        )
        self.quality_menu.pack(pady=5)
        self.quality_menu.set(self.quality)

        # PLAYLIST
        ctk.CTkLabel(self.settings_frame, text="Playlist").pack(pady=5)

        self.playlist_var = ctk.BooleanVar(value=self.data["settings"].get("playlist", False))

        self.playlist_switch = ctk.CTkSwitch(
            self.settings_frame,
            text="Download playlist",
            variable=self.playlist_var,
            command=self.toggle_playlist
        )
        self.playlist_switch.pack(pady=5)

        # THEME
        ctk.CTkLabel(self.settings_frame, text="Theme").pack(pady=5)
        self.theme_menu_settings = ctk.CTkOptionMenu(
            self.settings_frame,
            values=list(themes.keys()),
            command=self.change_theme
        )
        self.theme_menu_settings.pack(pady=5)

        # FOLDER
        self.folder_btn = ctk.CTkButton(
            self.settings_frame,
            text="Choose download folder",
            command=self.choose_folder,
            fg_color=self.current_color
        )
        self.folder_btn.pack(pady=10)

        self.folder_label = ctk.CTkLabel(
            self.settings_frame,
            text=f"📂 {self.download_path}",
            wraplength=200,
            justify="center"
        )
        self.folder_label.pack(pady=5)

        # ===== MAIN UI =====
        self.left_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_frame = ctk.CTkFrame(self.main_container, width=300)

        self.right_frame.pack(side="right", fill="y", padx=10, pady=20)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        # SETTINGS BTN
        self.settings_btn = ctk.CTkButton(
            self.left_frame,
            text="⚙️",
            width=40,
            fg_color=self.current_color,
            command=self.toggle_settings
        )
        self.settings_btn.pack(anchor="nw", pady=5)

        # TITLE
        frame_title = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        frame_title.pack(pady=10)

        self.icon_img = ctk.CTkImage(Image.open(icon_images["Ruby"]), size=(24, 24))
        self.icon_label = ctk.CTkLabel(frame_title, image=self.icon_img, text="")
        self.icon_label.pack(side="left", padx=5)

        self.title_label = ctk.CTkLabel(
            frame_title,
            text="RubyYT Downloader",
            font=("Arial", 20),
            text_color=self.current_color
        )
        self.title_label.pack(side="left")

        # URL
        self.entry = ctk.CTkEntry(self.left_frame, width=420, placeholder_text="Paste a link...")
        self.entry.pack(pady=10)
        self.entry.bind("<KeyRelease>", self.on_url_change)

        # PREVIEW
        self.preview_label = ctk.CTkLabel(self.left_frame, text="No preview", text_color="gray")
        self.preview_label.pack()

        self.thumbnail_label = ctk.CTkLabel(self.left_frame, text="")
        self.thumbnail_label.pack(pady=5)

        # MODE
        self.option = ctk.CTkOptionMenu(self.left_frame, values=["MP3", "MP4"])
        self.option.pack(pady=10)

        # DOWNLOAD
        self.button = ctk.CTkButton(
            self.left_frame,
            text="Download",
            command=self.start_download,
            fg_color=self.current_color,
            hover_color=darker(self.current_color)
        )
        self.button.pack(pady=10)

        # PROGRESS
        self.progress = ctk.CTkProgressBar(self.left_frame, width=420)
        self.progress.pack(pady=10)
        self.progress.set(0)

        # HISTORY
        self.history_title = ctk.CTkLabel(self.right_frame, text="History", font=("Arial", 16, "bold"))
        self.history_title.pack(pady=10)

        self.history_frame = ctk.CTkScrollableFrame(self.right_frame, width=260, height=350)
        self.history_frame.pack(padx=10, pady=10)

        self.clear_button = ctk.CTkButton(
            self.right_frame,
            text="Clear history",
            command=self.clear_history,
            fg_color=self.current_color,
            hover_color=darker(self.current_color)
        )
        self.clear_button.pack(pady=5)

        for item in self.data["history"]:
            self.display_history(item["title"], item["thumbnail"])

        self.change_theme(theme)

    # ===== SAFE THREAD =====
    def run_thread(self, target):
        threading.Thread(target=target, daemon=True).start()

    def safe_update(self, func):
        if self.winfo_exists():
            self.after(0, func)

    # ===== SETTINGS =====
    def toggle_playlist(self):
        self.data["settings"]["playlist"] = self.playlist_var.get()
        save_data(self.data)

    def choose_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.download_path = path
            self.folder_label.configure(text=f"📂 {path}")
            self.data["settings"]["download_path"] = path
            save_data(self.data)

    def toggle_settings(self):
        if self.settings_visible:
            self.settings_frame.pack_forget()
            self.settings_visible = False
        else:
            self.settings_frame.pack(side="left", fill="y", before=self.left_frame)
            self.settings_visible = True

    def set_quality(self, value):
        self.quality = value
        self.data["settings"]["quality"] = value
        save_data(self.data)

    # ===== PREVIEW =====
    def on_url_change(self, event):
        if self.preview_after_id:
            self.after_cancel(self.preview_after_id)
        self.preview_after_id = self.after(800, self.load_preview)

    def load_preview(self):
        url = self.entry.get()
        if not url:
            return

        def run():
            try:
                info = get_video_info(url)
                title = info.get("title", "Unknown")
                thumbnail = info.get("thumbnail")

                self.safe_update(lambda: self.preview_label.configure(text=title))

                if thumbnail:
                    import requests
                    from io import BytesIO
                    img = Image.open(BytesIO(requests.get(thumbnail).content))
                    img = ctk.CTkImage(img, size=(200, 120))

                    self.safe_update(lambda: self.thumbnail_label.configure(image=img))
                    self.thumbnail_label.image = img
            except:
                self.safe_update(lambda: self.preview_label.configure(text="Erreur preview"))

        self.run_thread(run)

    # ===== DOWNLOAD =====
    def start_download(self):
        url = self.entry.get()
        mode = self.option.get()

        def run():
            try:
                info = get_video_info(url)
                title = info.get("title")
                thumb = info.get("thumbnail")

                download_video(
                    url,
                    self.download_path,
                    mode,
                    self.quality,
                    self.update_progress,
                    self.playlist_var.get()
                )

                self.safe_update(lambda: self.add_to_history(title, thumb))
            except:
                self.safe_update(lambda: self.preview_label.configure(text="❌ Erreur téléchargement"))

        self.run_thread(run)

    def update_progress(self, *args):
        value = args[0] if len(args) > 0 else 0
        self.safe_update(lambda: self.progress.set(value))

    # ===== HISTORY =====
    def display_history(self, title, thumbnail):
        item = ctk.CTkFrame(self.history_frame)
        item.pack(pady=5, fill="x")

        if thumbnail:
            import requests
            from io import BytesIO
            img = Image.open(BytesIO(requests.get(thumbnail).content))
            img = ctk.CTkImage(img, size=(80, 50))

            img_label = ctk.CTkLabel(item, image=img, text="")
            img_label.image = img
            img_label.pack(side="left", padx=5)

        title_label = ctk.CTkLabel(item, text=title, wraplength=150)
        title_label.pack(side="left")

    def add_to_history(self, title, thumbnail):
        self.data["history"].append({"title": title, "thumbnail": thumbnail})
        save_data(self.data)
        self.display_history(title, thumbnail)

    def clear_history(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        self.data["history"] = []
        save_data(self.data)

    # ===== THEME =====
    def change_theme(self, choice):
        self.current_color = themes[choice]

        self.title_label.configure(text_color=self.current_color)
        self.button.configure(fg_color=self.current_color, hover_color=darker(self.current_color))
        self.clear_button.configure(fg_color=self.current_color, hover_color=darker(self.current_color))
        self.settings_btn.configure(fg_color=self.current_color)
        self.folder_btn.configure(fg_color=self.current_color)

        self.progress.configure(progress_color=self.current_color)

        self.option.configure(
            fg_color=self.current_color,
            button_color=darker(self.current_color),
            button_hover_color=darker(self.current_color, 0.7)
        )

        self.quality_menu.configure(
            fg_color=self.current_color,
            button_color=darker(self.current_color),
            button_hover_color=darker(self.current_color, 0.7)
        )

        self.theme_menu_settings.configure(
            fg_color=self.current_color,
            button_color=darker(self.current_color),
            button_hover_color=darker(self.current_color, 0.7)
        )

        # UI ICON
        img = ctk.CTkImage(Image.open(icon_images[choice]), size=(24, 24))
        self.icon_label.configure(image=img)
        self.icon_label.image = img

        # WINDOWS ICON (STABLE)
        try:
            ico_path = f"assets/{choice.lower()}.ico"
            if os.path.exists(ico_path):
                self.iconbitmap(ico_path)
        except Exception as e:
            print("Icon error:", e)

        self.data["settings"]["theme"] = choice
        save_data(self.data)

        self.title_label.configure(text=f"{choice}YT Downloader")
        self.title(f"{choice}YT Downloader")