import pygame
import json
import math
import random
import os
from settings import *
from player import Player
from camera import Camera
from effects import draw_death_flash

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

screen_width = screen.get_width()
screen_height = screen.get_height()
clock = pygame.time.Clock()
pygame.display.set_caption("Platform")


font = pygame.font.SysFont(None, 100)
large_font = pygame.font.SysFont(None, 250)
small_font = pygame.font.SysFont(None, 40)

TILE_SIZE = screen_width // 10

MINIMAP_PADDING = 20
MINIMAP_HEIGHT = 140
MINIMAP_WIDTH = 220

MINIMAP_X = screen_width - MINIMAP_WIDTH - MINIMAP_PADDING
MINIMAP_Y = MINIMAP_PADDING

SAVE_FILE = "best_times.json"

exit_button_rect = pygame.Rect(screen_width//2 - 100, 600, 200, 60)
exit_button_colour = (200,50,50)
exit_button_hover_colour = (255,80,80)
exit_button_text = small_font.render("EXIT", True, (255,255,255))

tiles = []
spawn_points = []
death_tiles = []
power_ups = []
end_level = []
coins = []
coin_popups = []
heart_popups = []
lava_particles = []
end_particles = []
coin_particles = []
heart_particles = []

dirt = pygame.image.load("images/64x64_dirt.png").convert_alpha()
dirt = pygame.transform.scale(dirt, (TILE_SIZE, TILE_SIZE))

magma = pygame.image.load("images/64x64_magma.png").convert_alpha()
magma = pygame.transform.scale(magma, (TILE_SIZE, TILE_SIZE))

coin_img = pygame.image.load("images/tile_coin.png")
coin_img = pygame.transform.scale(coin_img, (48,48))

end_tile_img = pygame.image.load("images/end_tile.png")
end_tile_img = pygame.transform.scale(end_tile_img, (TILE_SIZE, TILE_SIZE))

heart_powerup = pygame.image.load("images/tile_heart.png")
heart_powerup = pygame.transform.scale(heart_powerup, (48,48))

player = Player(0,0,50,120, spawn_points)
camera = Camera(screen_width, screen_height, TILE_SIZE)

MAPS = ["maps/map1.json",
        "maps/map2.json",
        "maps/map3.json",
        "maps/map4.json",
]

best_times = {}

current_map_index = 0 
coin_count = 0
total_coins = 0
coin_timer = 0

shake_duration = 0
shake_magnitude = 5
shake_offset_x = 0
shake_offset_y = 0

exit_pulse = 0
game_state = "start"

def load_level(path, tile_size):
    global total_coins

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
                power_ups.append(pygame.Rect(center_x - 12, center_y - 12, 48,48))
            
            if tile == 5:
                end_level.append(rect)
            
            if tile == 6:
                center_x = rect.x + tile_size // 2
                center_y = rect.y + tile_size // 2
                coins.append(pygame.Rect(center_x - 12, center_y - 12, 24, 24))
            
    total_coins = len(coins)        
    return tiles, death_tiles, spawn_points, tilemap, end_level

def draw_start_screen(screen):
    overlay = pygame.Surface(screen.get_size())
    overlay.fill((50,120,255))
    screen.blit(overlay, (0,0))

    name = large_font.render("Deccy Reccy", True, (255,255,255))
    start = font.render("Press SPACE To Start", True, (255,255,255))
    rect = start.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 150))
    name_rect = name.get_rect(center=(screen.get_width()//2, screen.get_height()/2 - 250))
    screen.blit(start,rect)
    screen.blit(name, name_rect)

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

def level_end(screen, final_time_ms):
    overlay = pygame.Surface(screen.get_size())
    overlay.set_alpha(200)
    overlay.fill((50,50,50))
    screen.blit(overlay, (0,0))

    level_completed = font.render("LEVEL COMPLETED", True, (0,0,0))
    rect = level_completed.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 40))
    screen.blit(level_completed, rect)

    sub = small_font.render("Press Esc To Continue", True, (0,0,0))
    rect = sub.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
    screen.blit(sub, rect)

    elapsed_milliseconds = final_time_ms % 1000
    elapsed_seconds = (final_time_ms // 1000) % 60
    elapsed_minutes = (final_time_ms // 60000) % 60
    final_time_text = small_font.render(f"Final Time: {elapsed_minutes:02}:{elapsed_seconds:02}:{elapsed_milliseconds:03}", True, (255,255,255))
    screen.blit(final_time_text, (screen.get_width()/2 - final_time_text.get_width()//2, screen.get_height()//2 + 50))

def draw_map_select(screen, selected_index):
    screen.fill((30,30,30))

    title = font.render("SELECT MAP", True, (255,255,255))
    screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))

    for i, map_path in enumerate(MAPS):
        colour = (255,255,0) if i == selected_index else (200,200,200)
        text = small_font.render(f"Map {i+1}", True, colour)
        screen.blit(text, (screen.get_width()//2 - 60, 250 + i * 60))

        if i in best_times:
            time_text = small_font.render(f"Best: {format_time(best_times[i])}", True, (150,255,150))
        else: 
            time_text = small_font.render("Best: N/A", True, (150,255,150))
        screen.blit(time_text, (screen.get_width()//2 + 60, 250 + i * 60))
    
    mouse_pos = pygame.mouse.get_pos()
    colour = exit_button_hover_colour if exit_button_rect.collidepoint(mouse_pos) else exit_button_colour
    pygame.draw.rect(screen, colour, exit_button_rect)
    screen.blit(exit_button_text, (exit_button_rect.centerx - exit_button_text.get_width()//2, exit_button_rect.centery - exit_button_text.get_height()//2)) 

def draw_minimap(screen, tilemap, player, scale_x, scale_y):
    minimap_surface = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT))
    minimap_surface.fill((20,20,20))

    for row_i, row in enumerate(tilemap):
        for col_i, tile in enumerate(row):
            if tile == 1:
                colour = (100, 50, 0)
            elif tile == 2:
                colour = (200, 60, 60)
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

def load_best_times():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
        except json.JSONDecodeError:
            return{}
    return {}

def save_best_times(best_times):
    with open(SAVE_FILE, "w") as f:
        json.dump(best_times, f)

def format_time(ms):
    elapsed_milliseconds = ms % 1000
    elapsed_seconds = (ms // 1000) % 60
    elapsed_minutes = (ms // 60000) % 60
    return f"{elapsed_minutes:02}:{elapsed_seconds:02}:{elapsed_milliseconds:03}"

player.respawn()
game_start_time = pygame.time.get_ticks()
best_times = load_best_times()

final_time_ms = 0
death_flash_alpha = 0
music_fade_time = 1000
music_volume = 0.5

running = True
level_finished = False
level_timer_running = True
current_music = None

while running:
    key = pygame.key.get_pressed()
    screen.fill((0,0,0))

    exit_pulse += 1
    coin_timer += 0.05

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "map_select":
                if exit_button_rect.collidepoint(event.pos):
                    running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state = "map_select"
            if event.key == pygame.K_SPACE and game_state == "playing":
                player.jump()
            if game_state == "game_over":
                if event.key == pygame.K_r:
                    player.current_health = player.max_health
                    if player.rect.top > len(tilemap) * TILE_SIZE or player.rect.colliderect(dt):
                        death_flash_alpha = 180
                        player.lose_life()
                        player.respawn()
                        shake_duration = 10
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
                coins.clear()
                coin_count = 0
                total_coins = 0

                tiles, death_tiles, spawn_points, tilemap, end_level = load_level(MAPS[current_map_index], TILE_SIZE)
                player.respawn()

                game_start_time = pygame.time.get_ticks()
                level_timer_running = True
                game_state = "playing"
    
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

    if game_state == "level_complete":
        level_end(screen, final_time_ms)
        clock.tick(60)
        pygame.display.flip()
        continue

    for tile in tiles:
        screen.blit(dirt, (tile.x - camera.offset_x, tile.y - camera.offset_y))

    for tile in death_tiles:
        if random.random() < 0.04:
            lava_particles.append({
                "x": tile.left + random.randint(4, TILE_SIZE - 4),
                "y": tile.top + random.randint(-2, 2),
                "vx": random.uniform(-0.5, 0.5),
                "vy": random.uniform(-2,-1),
                "life": random.randint(20,40),
                "size": random.randint(5,12)
            })

        screen.blit(magma, (tile.x - camera.offset_x, tile.y - camera.offset_y))

    for tile in end_level:
        screen.blit(end_tile_img, (tile.x - camera.offset_x, tile.y - camera.offset_y))
        if random.random() < 0.04:
            angle = random.uniform(0,2 * math.pi)
            speed = random.uniform(1,3)

            end_particles.append({
                "x": tile.centerx,
                "y": tile.centery - 15,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.randint(20,40),
                "size": random.randint(12,15)
            })

        if coin_count < total_coins:
            locked = end_tile_img.copy()
            locked.set_alpha(100)
            screen.blit(locked, (tile.x - camera.offset_x, tile.y -camera.offset_y))

    for c in coins:
        if random.random() < 0.04:
            angle = random.uniform(0,2 * math.pi)
            speed = random.uniform(1,3)

            coin_particles.append({
                "x": c.centerx,
                "y": c.centery,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.randint(20,40),
                "size": random.randint(8,12)
            })

        float_offset = math.sin(coin_timer + c.x * 0.01 + c.y * 0.01) * 5
        screen.blit(coin_img, (c.x - camera.offset_x, c.y - camera.offset_y + float_offset))

        if player.rect.colliderect(c):
            coin_count += 1
            coin_popups.append({"x": c.x, "y": c.y, "alpha": 255})
            coins.remove(c)

    for p in power_ups:
        if random.random() < 0.04:
            angle = random.uniform(0,2*math.pi)
            speed = random.uniform(1,3)

            heart_particles.append({
                "x": p.centerx,
                "y": p.centery,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.randint(20,40),
                "size": random.randint(8,12)
            })

        float_offset = math.sin(coin_timer + p.x * 0.01 + p.y * 0.01) * 5
        screen.blit(heart_powerup, (p.x - camera.offset_x, p.y - camera.offset_y + float_offset))

        if player.rect.colliderect(p):
            player.gain_life()
            player.start_green_flash()
            heart_popups.append({"x": p.x, "y": p.y, "alpha": 255})
            power_ups.remove(p)
    
    for dt in death_tiles:
        if player.rect.colliderect(dt):
            if player.rect.top > len(tilemap) * TILE_SIZE or player.rect.colliderect(dt):
                death_flash_alpha = 180
                player.lose_life()
                player.respawn()
                shake_duration = 10
                break

        if player.rect.top > len(tilemap) * TILE_SIZE:
            death_flash_alpha = 180
            player.lose_life()
            player.respawn()
            shake_duration = 10

    for p in lava_particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.05
        p["life"] -= 0.5

        alpha = max(0, int(255 * (p["life"] / 40)))
        colour = (255, random.randint(80,120), 0)

        surf = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*colour, alpha), (p["size"], p["size"]), p["size"])

        screen.blit(surf, (p["x"] - camera.offset_x, p["y"] - camera.offset_y))

        if p["life"] <= 0:
            lava_particles.remove(p)

    for p in end_particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 1

        alpha = max(0, int(255 * (p["life"] / 40)))
        colour = (20, 145, random.randint(20,77))

        surf = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*colour, alpha), (p["size"], p["size"]), p["size"])
        screen.blit(surf, (p["x"] - camera.offset_x, p["y"] - camera.offset_y))

        if p["life"] <= 0:
            end_particles.remove(p)

    for p in coin_particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 1

        if p["life"] <= 0:
            coin_particles.remove(p)
            continue

        alpha = max(0, int(255 * (p["life"] / 40)))

        surf = coin_img.copy()
        surf.set_alpha(alpha)

        surf = pygame.transform.scale(surf, (p["size"]*2, p["size"]*2))
        screen.blit(surf, (p["x"] - camera.offset_x, p["y"] - camera.offset_y - p["size"]))


    for p in heart_particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 1

        if p["life"] <= 0:
            heart_particles.remove(p)
            continue

        alpha = max(0, int(255 * (p["life"] / 40)))

        surf = heart_powerup.copy()
        surf.set_alpha(alpha)

        surf = pygame.transform.scale(surf, (p["size"]*2, p["size"]*2))

        screen.blit(surf, (p["x"] - camera.offset_x - p["size"], p["y"] - camera.offset_y - p["size"]))

    if player.rect.top > len(tilemap) * TILE_SIZE:
        if player.rect.top > len(tilemap) * TILE_SIZE or player.rect.colliderect(dt):
            death_flash_alpha = 180
            player.lose_life()
            player.respawn()
            shake_duration = 10

        death_flash_alpha = 180
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
        screen.blit(player.current_image, (player.rect.x - camera.offset_x, player.rect.bottom - player.current_image.get_height() - camera.offset_y))
        player.draw_health_bar(screen, 20,20)
 
        map_width = len(tilemap[0]) * TILE_SIZE
        map_height = len(tilemap) * TILE_SIZE
        camera.update(player, map_width, map_height)

        scale_x = MINIMAP_WIDTH  / map_width
        scale_y = MINIMAP_HEIGHT / map_height

        draw_minimap(screen, tilemap, player, scale_x, scale_y)

        coin_text = small_font.render(f"Coins: {coin_count}/{total_coins}", True, (255,215, 0))
        screen.blit(coin_text, (20, 60))

        for popup in coin_popups[:]:
            popup["y"] -= 1
            popup["alpha"] -= 6

            surf = small_font.render("+1", True, (255,215, 0))
            surf.set_alpha(popup["alpha"])
            screen.blit(surf, (popup["x"] - camera.offset_x, popup["y"] - camera.offset_y))
            if popup["alpha"] <= 0:
                coin_popups.remove(popup)
        
        for popup in heart_popups[:]:
            popup["y"] -= 1
            popup["alpha"] -= 6

            surf = small_font.render("+1", True, (255,40, 40))
            surf.set_alpha(popup["alpha"])
            screen.blit(surf, (popup["x"] - camera.offset_x, popup["y"] - camera.offset_y))
            if popup["alpha"] <= 0:
                heart_popups.remove(popup)

        for end in end_level:
            if player.rect.colliderect(end) and coin_count >= total_coins:
                if level_timer_running:
                    current_time = pygame.time.get_ticks()
                    final_time_ms = current_time  -game_start_time
                    level_timer_running = False

                    if current_map_index not in best_times or final_time_ms < best_times[current_map_index]:
                        best_times[current_map_index] = final_time_ms
                        save_best_times(best_times)

                game_state = "level_complete"
                tiles.clear()
                death_tiles.clear()
                spawn_points.clear()
                power_ups.clear()
                coins.clear()
                coin_popups.clear()
                coin_count = 0
                total_coins = 0
                if key [pygame.K_RETURN]:
                    game_state = "map_select"

    if level_timer_running:
        current_time = pygame.time.get_ticks()
        elapsed_ms = current_time - game_start_time
    else:
        elapsed_ms = final_time_ms

    elapsed_seconds = (elapsed_ms // 1000) % 60
    elapsed_minutes = (elapsed_ms // 60000) % 60
    elapsed_milliseconds = elapsed_ms % 1000

    timer_text = small_font.render(f"{elapsed_minutes:02}:{elapsed_seconds:02}:{elapsed_milliseconds:03}", True, (255,255,255))
    screen.blit(timer_text, (1500,25))

    if game_state == "game_over":
        draw_game_over(screen)

    draw_death_flash(screen, death_flash_alpha)

    death_flash_alpha -= 180 / DEATH_FLASH_DURATION
    death_flash_alpha = max(0, int(death_flash_alpha))

    clock.tick(60)
    pygame.display.flip()
pygame.quit()