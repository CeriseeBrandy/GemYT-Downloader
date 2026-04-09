import customtkinter as ctk
from PIL import Image, ImageEnhance
from ui import App

ctk.set_appearance_mode("dark")


class Splash(ctk.CTk):

    def __init__(self):
        super().__init__()

        # COLORS
        self.bg_color = "#242424"
        self.theme_color = "#FF3B3B"

        self.geometry("450x400")
        self.overrideredirect(True)

        # CENTER
        self.update_idletasks()
        w, h = 450, 400
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.configure(fg_color=self.bg_color)

        # animation vars
        self.scale = 1.0
        self.direction = 1
        self.alpha = 0

        # LOGO
        self.base_img = Image.open("assets/ruby.png")

        self.logo = ctk.CTkLabel(self, text="")
        self.logo.pack(pady=40)

        # TITLE (simple rouge)
        self.full_text = "RubyYT Downloader"
        self.current_text = ""

        self.title_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 22, "bold"),
            text_color=self.theme_color
        )
        self.title_label.pack(pady=5)

        # SUBTEXT
        self.subtitle = ctk.CTkLabel(
            self,
            text="Initializing...",
            font=("Arial", 12),
            text_color=self.theme_color
        )
        self.subtitle.pack()

        # PROGRESS
        self.progress = ctk.CTkProgressBar(self, width=250)
        self.progress.pack(pady=20)
        self.progress.set(0)
        self.progress.configure(progress_color=self.theme_color)

        # START
        self.attributes("-alpha", 0)
        self.fade_in()

        self.animate_logo()
        self.animate_progress()
        self.type_text()

    # ===== FADE IN =====
    def fade_in(self):
        if self.alpha < 1:
            self.alpha += 0.03
            self.attributes("-alpha", self.alpha)
            self.after(20, self.fade_in)

    # ===== FADE OUT =====
    def fade_out(self):
        if self.alpha > 0:
            self.alpha -= 0.03
            self.attributes("-alpha", self.alpha)
            self.after(20, self.fade_out)
        else:
            self.launch_app()

    # ===== TYPE TEXT =====
    def type_text(self):
        if len(self.current_text) < len(self.full_text):
            self.current_text += self.full_text[len(self.current_text)]
            self.title_label.configure(text=self.current_text)
            self.after(40, self.type_text)

    # ===== LOGO ANIMATION =====
    def animate_logo(self):
        if self.scale >= 1.08:
            self.direction = -1
        elif self.scale <= 0.92:
            self.direction = 1

        self.scale += 0.01 * self.direction

        size = int(130 * self.scale)

        img = self.base_img.resize((size, size))

        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.1)

        img_ctk = ctk.CTkImage(img, size=(size, size))

        self.logo.configure(image=img_ctk)
        self.logo.image = img_ctk

        self.after(30, self.animate_logo)

    # ===== PROGRESS =====
    def animate_progress(self):
        current = self.progress.get()

        if current < 1:
            self.progress.set(current + 0.015)
            self.after(40, self.animate_progress)
        else:
            self.after(400, self.fade_out)

    # ===== LAUNCH =====
    def launch_app(self):
        self.destroy()
        app = App()
        app.mainloop()


if __name__ == "__main__":
    splash = Splash()
    splash.mainloop()