import pygame
import json

pygame.init()

screen_width, screen_height = 1920,1080

screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
pygame.display.set_caption("Map builder")

current_map_name = "map1"
tilemap = []

ROWS = 20
COLS = 50

TILE_SIZE = 64
RESET_RECT = pygame.Rect(1720,20,160,50)

dirt = pygame.image.load("images/64x64_dirt.png")
magma = pygame.image.load("images/64x64_magma.png")
spawn = pygame.image.load("images/spawn_block.png")
health_powerup = pygame.image.load("images/health_powerup.png")
end_tile = pygame.image.load("images/end_tile.png")
coin_img = pygame.image.load("images/coin.png")

TILE_NAMES =  {
    0: "Empty",
    1: "Dirt",
    2: "Magma",
    3: "Spawn",
    4: "Health",
    5: "End",
    6: "Coin"
}

Tile_IMAGES = {
    1: dirt,
    2: magma,
    3: spawn,
    4: health_powerup,
    5: end_tile,
    6: coin_img
}
font = pygame.font.SysFont(None, 32)

camera_x = 0
camera_y = 0
SCROLL_SPEED = 10

max_camera_x = max(0, COLS * TILE_SIZE - screen_width)
max_camera_y = max(0, ROWS * TILE_SIZE - screen_height)

#colours

WHITE = (255,255,255)
BLACK = (0,0,0)
GREY = (200,200,200)
RED = (255,0,0)
BROWN = (100,50, 0)

mouse_down = False
is_saved = True

paint_value = 1
current_paint_value = paint_value

def draw_grid():
    for row in range(ROWS):
        for col in range(COLS):
            world_x = col * TILE_SIZE
            world_y = row * TILE_SIZE

            screen_y = world_y - camera_y
            screen_x = world_x - camera_x

            if screen_x + TILE_SIZE < 0 or screen_x > screen_width:
                continue
            if screen_y + TILE_SIZE < 0 or screen_y > screen_height:
                continue

            rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)

            if tilemap[row][col] == 1:
                screen.blit(dirt, rect)
            elif tilemap[row][col] == 2:
                screen.blit(magma, rect)
            elif tilemap[row][col] == 3:
                screen.blit(spawn, rect)
            elif tilemap[row][col] == 4:
                screen.blit(health_powerup, rect)
            elif tilemap[row][col] == 5:
                screen.blit(end_tile, rect)
            elif tilemap[row][col] == 6:
                screen.blit(coin_img, rect)
            else:
                colour = WHITE

            pygame.draw.rect(screen, GREY, rect, 1)

def paint_tile(pos):
    global is_saved

    x,y = pos

    world_x = x + camera_x
    world_y = y + camera_y

    col = world_x // TILE_SIZE
    row = world_y // TILE_SIZE

    if 0 <= row < ROWS and 0 <= col < COLS:
        if paint_value == 3:
            for r in range(ROWS):
                for c in range(COLS):
                    if tilemap[r][c] == 3:
                        tilemap[r][c] = 0
        
        tilemap[row][col] = paint_value
        is_saved = False

def save_map():
    global is_saved
    filename = f"maps/{current_map_name}.json"
    with open(filename, "w") as f:
        json.dump(tilemap, f)
    is_saved = True
    print(f"saved {filename}")

def load_map():
    global tilemap, is_saved
    filename = f"maps/{current_map_name}.json"

    try:
        with open(filename, "r") as f:
            tilemap = json.load(f)
        is_saved = True

    except FileNotFoundError:
        tilemap = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        is_saved = False

def clamp_camera():
    global camera_x, camera_y
    camera_x = max(0, min(camera_x, max_camera_x))
    camera_y = max(0, min(camera_y, max_camera_y))

def draw_status_text():
    status_text = "SAVED" if is_saved else "UNSAVED"
    colour = (0,200,0) if is_saved else(200,0,0)

    map_surf = font.render(f"Map: {current_map_name}", True, (255,255,255))
    status_surf = font.render(f"Status: {status_text}", True, colour)
    
    screen.blit(map_surf, (10,10))
    screen.blit(status_surf, (10,45))

    tile_name = TILE_NAMES.get(paint_value, "Unknown")
    tile_text = font.render(f"Selected: {tile_name}", True, (255,255,255))

    screen.blit(tile_text, (10,85))

    tile_img = Tile_IMAGES.get(paint_value)
    if tile_img:
        screen.blit(tile_img, (10,120))

def reset_map():
    global tilemap
    tilemap = [[0 for _ in range(COLS)] for _ in range(ROWS)]
running = True

load_map()


while running:
    screen.fill(BROWN)

    draw_status_text()
    draw_grid()
    
    keys = pygame.key.get_pressed()
    current_paint_value = paint_value
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_down = True
                paint_tile(event.pos)
            elif event.button == 3:
                mouse_down = True
                paint_value = 0
                paint_tile(event.pos)
            if event.button == 1:
                if RESET_RECT.collidepoint(event.pos):
                    reset_map()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button in (1,3):
                mouse_down = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_p:
                paint_value = 1
            if event.key == pygame.K_o:
                paint_value = 2
            if event.key == pygame.K_i:
                paint_value = 3
            if event.key == pygame.K_u:
                paint_value = 4
            if event.key == pygame.K_y:
                paint_value = 5
            if event.key == pygame.K_t:
                paint_value = 6
            
            if event.key == pygame.K_1:
                current_map_name = "map1"
                load_map()
            if event.key == pygame.K_2:
                current_map_name = "map2"
                load_map()
            if event.key == pygame.K_3:
                current_map_name = "map3"
                load_map()
            if event.key == pygame.K_4:
                current_map_name = "map4"
                load_map()
            if event.key == pygame.K_5:
                current_map_name = "map5"
                load_map()
            
            if event.key == pygame.K_F5:
                save_map()

            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_LCTRL] and keys[pygame.K_r]:
                reset_map()

    if keys[pygame.K_a]:
        camera_x -= SCROLL_SPEED
    if keys[pygame.K_d]:
        camera_x += SCROLL_SPEED
    
    if keys[pygame.K_w]:
        camera_y -= SCROLL_SPEED
    if keys[pygame.K_s]:
        camera_y += SCROLL_SPEED
    
    pygame.draw.rect(screen, (200,50,50), RESET_RECT, border_radius=5)
    reset_text = font.render("RESET MAP", True, (255,255,255))
    text_rect = reset_text.get_rect(center=RESET_RECT.center)
    screen.blit(reset_text, text_rect)

    if RESET_RECT.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, (230,80,80), RESET_RECT, border_radius=5)
    clamp_camera()

    if mouse_down:
        paint_tile(pygame.mouse.get_pos())

    pygame.display.flip()
pygame.quit()
