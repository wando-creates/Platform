import pygame
import json

pygame.init()

screen_width, screen_height = 1920,1080

screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
pygame.display.set_caption("Map builder")

current_map_name = "map1"

ROWS = 20
COLS = 50

TILE_SIZE = 64

dirt = pygame.image.load("images/64x64_dirt.png")
magma = pygame.image.load("images/64x64_magma.png")
spawn = pygame.image.load("images/spawn_block.png")
health_powerup = pygame.image.load("images/health_powerup.png")
end_tile = pygame.image.load("images/end_tile.png")

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

tilemap = [[0 for _ in range(COLS)] for _ in range(ROWS)]

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
running = True

while running:
    screen.fill(BROWN)
    draw_grid()
    draw_status_text()
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
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button in (1,3):
                mouse_down = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_i:
                paint_value = 1
            if event.key == pygame.K_o:
                paint_value = 2
            if event.key == pygame.K_p:
                paint_value = 3
            if event.key == pygame.K_u:
                paint_value = 4
            if event.key == pygame.K_y:
                paint_value = 5
            
            if event.key == pygame.K_1:
                current_map_name = "map1"
            if event.key == pygame.K_2:
                current_map_name = "map2"
            if event.key == pygame.K_3:
                current_map_name = "map3"
            
            if event.key == pygame.K_F5:
                save_map()

    if keys[pygame.K_a]:
        camera_x -= SCROLL_SPEED
    if keys[pygame.K_d]:
        camera_x += SCROLL_SPEED
    
    if keys[pygame.K_w]:
        camera_y -= SCROLL_SPEED
    if keys[pygame.K_s]:
        camera_y += SCROLL_SPEED
    
    clamp_camera()

    if mouse_down:
        paint_tile(pygame.mouse.get_pos())

    pygame.display.flip()
pygame.quit()
