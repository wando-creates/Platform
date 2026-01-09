import random

class Camera:
    def __init__(self, screen_width, screen_height, tile_size):
        self.offset_x = 0
        self.offset_y = 0

        self.dead_zone = tile_size * 2

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.tile_size = tile_size

        self.shake_intensity = 0
        self.shake_duration = 0

    def update(self,player,map_width,map_height):
        self.offset_x = player.rect.centerx - self.screen_width // 2
        self.offset_y = player.rect.centery - self.screen_height // 2
        self.offset_x = max(0, min(self.offset_x, map_width - self.screen_width))
        self.offset_y = max(0, min(self.offset_y, map_height - self.screen_height))

        shake_x, shake_y = self.apply_shake()
        self.offset_x += shake_x
        self.offset_y += shake_y
    
    def start_shake(self, intensity, duration):
        self.shake_intensity = intensity
        self.shake_duration = duration
    
    def apply_shake(self):
        if self.shake_duration > 0:
            self.shake_duration -= 1
            return (
                random.randint(-self.shake_intensity, self.shake_intensity),
                random.randint(-self.shake_intensity, self.shake_intensity)
            )
        return (0,0)