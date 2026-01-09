import pygame
import json
from settings import *
from player import Player
from camera import Camera
from effects import draw_death_flash

pygame.init()

screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

screen_width = screen.get_width()
screen_height = screen.get_height()
clock = pygame.time.Clock()
pygame.display.set_caption("Platform")

font = pygame.font.SysFont(None, 100)
small_font = pygame.font.SysFont(None, 40)

TILE_SIZE = screen_width // 10

MINIMAP_PADDING = 20
MINIMAP_HEIGHT = 140
MINIMAP_WIDTH = 220

MINIMAP_X = screen_width - MINIMAP_WIDTH - MINIMAP_PADDING
MINIMAP_Y = MINIMAP_PADDING

tiles = []
spawn_points = []
death_tiles = []
power_ups = []

dirt = pygame.image.load("images/64x64_dirt.png").convert_alpha()
dirt = pygame.transform.scale(dirt, (TILE_SIZE, TILE_SIZE))

magma = pygame.image.load("images/64x64_magma.png").convert_alpha()
magma = pygame.transform.scale(magma, (TILE_SIZE, TILE_SIZE))

health_powerup = pygame.image.load("images/health_powerup.png")
health_powerup = pygame.transform.scale(health_powerup, (24,24))

player = Player(0,0,50,120, spawn_points)
camera = Camera(screen_width, screen_height, TILE_SIZE)

MAPS = ["maps/map1.json",
        "maps/map2.json",
        "maps/map3.json",
]

current_map_index = 0 

game_state = "start"

def load_level(path, tile_size):
    with open(path) as f:
        tilemap = json.load(f)

    for row_i, row in enumerate(tilemap):
        for col_i, tile in enumerate(row):
            rect = pygame.Rect(col_i * tile_size, row_i * tile_size, tile_size, tile_size)
            if tile == 1:
                tiles.append(rect)

            if tile == 2:
                death_tiles.append(rect)
            
            if tile == 3:
                spawn_x = rect.x + tile_size // 2
                spawn_y = rect.y - 120
                spawn_points.append((spawn_x, spawn_y))
            
            if tile == 4:
                center_x = rect.x + tile_size // 2
                center_y = rect.y + tile_size // 2
                power_ups.append(pygame.Rect(center_x - 12, center_y - 12, 24, 24))
    
    return tiles, death_tiles, spawn_points, tilemap

def draw_start_screen(screen):
    overlay = pygame.Surface(screen.get_size())
    overlay.fill((50,120,255))
    screen.blit(overlay, (0,0))

    start = font.render("Press SPACE To Start", True, (255,255,255))
    rect = start.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 50))
    screen.blit(start,rect)

def draw_game_over(screen):
    overlay = pygame.Surface(screen.get_size())
    overlay.set_alpha(200)
    overlay.fill((0,0,0))
    screen.blit(overlay, (0,0))

    game_over = font.render("GAME OVER", True, (255,0,0))
    rect = game_over.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 50))
    screen.blit(game_over, rect)

    restart = small_font.render("Press R To Restart", True, (255,255,255))
    restart_rect = restart.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 40))
    screen.blit(restart, restart_rect)

def draw_map_select(screen, selected_index):
    screen.fill((30,30,30))

    title = font.render("SELECT MAP", True, (255,255,255))
    screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))

    for i, map_path in enumerate(MAPS):
        colour = (255,255,0) if i == selected_index else (200,200,200)
        text = small_font.render(f"Map {i+1}", True, colour)
        screen.blit(text, (screen.get_width()//2 - 60, 250 + i * 60))

def draw_minimap(screen, tilemap, player, scale_x, scale_y):
    minimap_surface = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT))
    minimap_surface.fill((20,20,20))

    for row_i, row in enumerate(tilemap):
        for col_i, tile in enumerate(row):
            if tile == 1:
                colour = (100, 50, 0)
            elif tile == 2:
                colour = (200, 60, 60)
            elif tile == 4:
                colour = (255,0,0)
            else:
                continue
                
            x = int(col_i * TILE_SIZE * scale_x)
            y = int(row_i * TILE_SIZE * scale_y)
            w = max(1, int(TILE_SIZE * scale_x))
            h = max(1, int(TILE_SIZE * scale_y))

            pygame.draw.rect(minimap_surface, colour, (x,y,w,h))
    
    player_x = int(player.rect.centerx * scale_x)
    player_y = int(player.rect.centery * scale_y)

    pygame.draw.circle(minimap_surface, (0,0,255), (player_x, player_y), 4)
    pygame.draw.rect(minimap_surface, (255,255,255), minimap_surface.get_rect(), 2)
    screen.blit(minimap_surface, (MINIMAP_X, MINIMAP_Y))

tiles, death_tiles, spawn_points, tilemap = load_level("maps/map1.json", TILE_SIZE)

player.respawn()

death_flash_alpha = 0

running = True

while running:
    key = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE and game_state == "playing":
                player.jump()
            if game_state == "game_over":
                if event.key == pygame.K_r:
                    player.current_health = player.max_health
                    player.respawn()
                    game_state = "playing"
            if game_state == "start" and event.key == pygame.K_SPACE:
                game_state = "map_select"
            if event.key == pygame.K_w and game_state == "playing":
                player.dash()
                player.create_shadows()
                player.draw_shadows(screen,camera)
            
            if game_state == "map_select":
                if event.key == pygame.K_UP:
                    current_map_index = (current_map_index - 1)
                if event.key == pygame.K_DOWN:
                    current_map_index = (current_map_index + 1)
            
            if event.key == pygame.K_RETURN:
                tiles.clear()
                death_tiles.clear()
                spawn_points.clear()

                tiles, death_tiles, spawn_points, tilemap = load_level(MAPS[current_map_index], TILE_SIZE)
                player.respawn()
                game_state = "playing"
    
    screen.fill(WHITE)

    if game_state == "start":
        draw_start_screen(screen)
        clock.tick(60)
        pygame.display.flip()
        continue
    
    if game_state == "map_select":
        draw_map_select(screen, current_map_index)
        clock.tick(60)
        pygame.display.flip()
        continue

    for tile in tiles:
        screen.blit(dirt, (tile.x - camera.offset_x, tile.y - camera.offset_y))

    for tile in death_tiles:
        screen.blit(magma, (tile.x - camera.offset_x, tile.y - camera.offset_y))

    for dt in death_tiles:
        if player.rect.colliderect(dt):
            death_flash_alpha = 180
            player.lose_life()
            player.respawn()
            break

    for p in power_ups:
        screen.blit(health_powerup, (p.x - camera.offset_x, p.y - camera.offset_y))
    
    for p in power_ups:
        if player.rect.colliderect(p):
            player.gain_life()
            player.start_green_flash()
            power_ups.remove(p)

    if player.rect.top > len(tilemap) * TILE_SIZE:
        death_flash_alpha = 180
        #camera.start_shake(intensity=12, duration=20)
        player.lose_life()
        player.respawn()

    if player.current_health <= 0:
        game_state = "game_over"
        player.max_health == 2
        player.current_health == player.max_health

    if game_state == "playing":    
        player.move()
        player.update(tiles)
        player.update_health_fade()
        player.draw_shadows(screen, camera)
        pygame.draw.rect(screen, player.colour, pygame.Rect(player.rect.x - camera.offset_x, player.rect.y - camera.offset_y, player.rect.width, player.rect.height))
        player.draw_health_bar(screen, 20,20)

        map_width = len(tilemap[0]) * TILE_SIZE
        map_height = len(tilemap) * TILE_SIZE
        camera.update(player, map_width, map_height)

        scale_x = MINIMAP_WIDTH / map_width
        scale_y = MINIMAP_HEIGHT / map_height

        draw_minimap(screen, tilemap, player, scale_x, scale_y)

    if game_state == "game_over":
        draw_game_over(screen)

    draw_death_flash(screen, death_flash_alpha)

    death_flash_alpha -= 180 / DEATH_FLASH_DURATION
    death_flash_alpha = max(0, int(death_flash_alpha))


    clock.tick(60)
    pygame.display.flip()
pygame.quit()