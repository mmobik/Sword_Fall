import pygame
import os


class SoundManager:
    def __init__(self):
        self.button_click_sound = self.load_sound("Sounds/Game_sounds/Button.mp3")
        self.current_music = None

    @staticmethod
    def load_sound(path):
        full_path = os.path.join("assets", path)
        try:
            return pygame.mixer.Sound(full_path)
        except pygame.error as e:
            print(f"Ошибка загрузки звука: {full_path}, {e}")
            return None

    def play_button_click(self):
        if self.button_click_sound:
            self.button_click_sound.play()

    def play_music(self, music_path):
        full_path = os.path.join("assets", "Sounds", music_path)
        if self.current_music != full_path:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            try:
                pygame.mixer.music.load(full_path)
                pygame.mixer.music.play(-1)
                self.current_music = full_path
            except pygame.error as e:
                print(f"Ошибка загрузки музыки: {full_path}, {e}")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_music = None
