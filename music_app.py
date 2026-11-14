import customtkinter as ctk
from PIL import Image, ImageDraw
import pygame
import os
import threading
import urllib.request
import io
import tempfile

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")
pygame.mixer.init()

TRACKS = [
    {"title": "Neon Drive", "artist": "Synthwave", "color": "#ff00ea", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"},
    {"title": "Cyber City", "artist": "Dark Wave", "color": "#00f3ff", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"},
    {"title": "Night Runner", "artist": "Retro Beat", "color": "#ffaa00", "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"}
]

class MusicApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GITHUB MUSIC PLAYER")
        self.geometry("900x600")
        self.configure(fg_color="#0a0a14")
        
        self.current_track_index = 0
        self.is_playing = False
        self.current_temp_file = None

        self.setup_ui()
        self.load_track(0)

    def setup_ui(self):
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color="#12121e")
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="MUSIC", font=ctk.CTkFont(size=20, weight="bold"), text_color="#00f3ff").pack(pady=20)

        self.scroll_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.track_buttons = []
        for i, track in enumerate(TRACKS):
            btn = ctk.CTkButton(self.scroll_frame, text=f"{track['title']}\n{track['artist']}", fg_color="transparent", hover_color="#1f1f2e", anchor="w", command=lambda idx=i: self.load_track(idx))
            btn.pack(fill="x", pady=5)
            self.track_buttons.append(btn)

        self.main_frame = ctk.CTkFrame(self, fg_color="#0a0a14")
        self.main_frame.pack(side="right", fill="both", expand=True)

        self.cover_label = ctk.CTkLabel(self.main_frame, text="")
        self.cover_label.pack(pady=(50, 20))

        self.title_label = ctk.CTkLabel(self.main_frame, text="", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.pack(pady=5)
        
        self.artist_label = ctk.CTkLabel(self.main_frame, text="", text_color="gray")
        self.artist_label.pack(pady=5)

        self.controls_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.controls_frame.pack(pady=30)

        ctk.CTkButton(self.controls_frame, text="⏮", width=50, height=50, fg_color="transparent", command=self.prev_track).pack(side="left", padx=20)
        self.play_btn = ctk.CTkButton(self.controls_frame, text="▶", width=70, height=70, fg_color="#00f3ff", text_color="black", command=self.toggle_play)
        self.play_btn.pack(side="left", padx=20)
        ctk.CTkButton(self.controls_frame, text="⏭", width=50, height=50, fg_color="transparent", command=self.next_track).pack(side="left", padx=20)

        self.status_label = ctk.CTkLabel(self.main_frame, text="Нажмите Play", text_color="gray")
        self.status_label.pack(side="bottom", pady=20)

    def generate_cover(self, color):
        img = Image.new("RGB", (300, 300), "#12121e")
        draw = ImageDraw.Draw(img)
        draw.ellipse((50, 50, 250, 250), fill=color, outline="white", width=5)
        draw.ellipse((100, 100, 200, 200), fill="#0a0a14")
        return ctk.CTkImage(light_image=img, size=(300, 300))

    def load_track(self, index):
        self.current_track_index = index
        track = TRACKS[index]
        self.title_label.configure(text=track["title"])
        self.artist_label.configure(text=track["artist"])
        self.cover_label.configure(image=self.generate_cover(track["color"]))
        
        for i, btn in enumerate(self.track_buttons):
            btn.configure(fg_color="#1f1f2e" if i == index else "transparent")

        pygame.mixer.music.stop()
        self.is_playing = False
        self.play_btn.configure(text="▶")
        self.download_and_play(track["audio_url"])

    def download_and_play(self, url):
        self.status_label.configure(text="Загрузка...", text_color="yellow")
        def bg_download():
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    audio_data = response.read()

                if self.current_temp_file and os.path.exists(self.current_temp_file):
                    os.remove(self.current_temp_file)
                
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                temp_file.write(audio_data)
                temp_file.close()
                self.current_temp_file = temp_file.name
                self.status_label.configure(text="Готово", text_color="#00f3ff")
            except Exception as e:
                self.status_label.configure(text=f"Ошибка: {e}", text_color="red")

        threading.Thread(target=bg_download, daemon=True).start()

    def toggle_play(self):
        if not self.current_temp_file: return
        if self.is_playing:
            pygame.mixer.music.pause()
            self.play_btn.configure(text="▶")
            self.is_playing = False
        else:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(self.current_temp_file)
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()
            self.play_btn.configure(text="⏸")
            self.is_playing = True
            self.check_music_end()

    def check_music_end(self):
        if self.is_playing and not pygame.mixer.music.get_busy():
            self.next_track()
        elif self.is_playing:
            self.after(1000, self.check_music_end)

    def next_track(self):
        self.load_track((self.current_track_index + 1) % len(TRACKS))
        self.toggle_play()

    def prev_track(self):
        self.load_track((self.current_track_index - 1) % len(TRACKS))
        self.toggle_play()

if __name__ == "__main__":
    app = MusicApp()
    app.mainloop()
