import pygame
from core.config import config

class Renderer:
    def __init__(self, game):
        self.game = game

    def render_game(self):
        if not self.game.player or not self.game.camera or not self.game.level or not self.game.level_renderer or not self.game.all_sprites:
            return
        self.game.level_renderer.render(self.game.virtual_screen)
        for sprite in self.game.all_sprites:
            self.game.virtual_screen.blit(sprite.image, self.game.camera.apply(sprite.rect))
        if config.DEBUG_MODE:
            pygame.draw.rect(self.game.virtual_screen, (0, 255, 0), self.game.camera.apply(self.game.player.hitbox), 1)
            if self.game.collision_objects:
                for obj in self.game.collision_objects:
                    pygame.draw.rect(self.game.virtual_screen, (255, 0, 0), self.game.camera.apply(obj['rect']), 1)
        self.game.level_renderer.render_overlap_tiles(
            self.game.virtual_screen,
            (self.game.player.hitbox.centerx, self.game.player.hitbox.centery)
        )
        if config.DEBUG_MODE:
            self._draw_debug_info()

    def _draw_debug_info(self):
        debug_text = [
            f"FPS: {self.game.clock.get_fps():.1f}",
            f"State: {self.game.game_state_manager.game_state}",
            f"Player Pos: {self.game.player.rect.topleft if self.game.player else 'N/A'}",
            f"Player Hitbox: {self.game.player.hitbox.topleft if self.game.player else 'N/A'}",
            f"Hitbox Size: {self.game.player.hitbox.size if self.game.player else 'N/A'}",
            f"Camera Offset: {self.game.camera.offset if self.game.camera else 'N/A'}",
            f"Frame: {self.game.player.current_frame if self.game.player else 'N/A'}",
            f"Anim State: {self.game.player.state_name if self.game.player else 'N/A'}",
            f"Objects: {len(self.game.collision_objects) if self.game.collision_objects else 0}",
        ]
        for i, text in enumerate(debug_text):
            surface = self.game.debug_font.render(text, True, (255, 255, 255))
            self.game.virtual_screen.blit(surface, (10, 10 + i * 20)) 