class Camera:
    def __init__(self, screen_width, screen_height, tile_size):
        self.offset_x = 0
        self.offset_y = 0

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.tile_size = tile_size

    def update(self,player,map_width,map_height):
        self.offset_x = player.rect.centerx - self.screen_width // 2
        self.offset_y = player.rect.centery - self.screen_height // 2
        self.offset_x = max(0, min(self.offset_x, map_width - self.screen_width))
        self.offset_y = max(0, min(self.offset_y, map_height - self.screen_height))
