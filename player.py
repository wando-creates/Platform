import pygame
import random
from settings import *

pygame.init()

class Player:
    def __init__(self, x, y, width, height, spawn_points):
        self.rect = pygame.Rect(x,y, width, height)
    
        self.idle_right = pygame.image.load("images/bob_i.png").convert_alpha()
        self.idle_left = pygame.image.load("images/bob_i_s.png").convert_alpha()

        self.idle_right_2 = pygame.image.load("images/bob.png").convert_alpha()
        self.idle_left_2 = pygame.image.load("images/bob_s.png").convert_alpha()

        self.running_right = pygame.image.load("images/bob_r.png").convert_alpha()
        self.running_left = pygame.image.load("images/bob_r_s.png").convert_alpha()

        self.jumping_right = pygame.image.load("images/bob_j.png").convert_alpha()
        self.jumping_left = pygame.image.load("images/bob_j_s.png").convert_alpha()

        self.jumping_right_2 = pygame.image.load("images/bob_j2.png").convert_alpha()
        self.jumping_left_2 = pygame.image.load("images/bob_j2_s.png").convert_alpha()

        self.current_image = self.idle_right

        self.sprite_offset_y = self.current_image.get_height() - self.rect.height
        self.colour = BLUE
        self.facing = "right"

        self.max_health = 2
        self.current_health = self.max_health

        self.velocity_x = 0
        self.velocity_y = 0

        self.speed = SPEED
        self.jump_power = JUMP_POWER
        self.gravity = GRAVITY

        self.max_jumps = MAX_JUMPS
        self.jumps_left = self.max_jumps
        self.on_ground = False

        self.dash_speed = 100
        self.dash_time = 8
        self.dash_timer = 0
        self.dash_cooldown = 40
        self.dash_cooldown_timer = 0
        self.is_dashing = False

        self.life_fades = [255] * self.max_health
        self.fade_speed = 10

        self.flash_timer = 0
        self.flash_colour = None

        self.shadows = []
        self.shadow_lifetime = SHADOW_LIFETIME
        self.shadow_cooldown = 0
        self.shadow_burst_left = 0

        self.spawn_points = spawn_points

        self.on_left_wall = False
        self.on_right_wall = False
        self.wall_jump_power_x = 15
        self.wall_jump_power_y = -25

        self.state = "idle"
        self.last_facing = "right"
        self.anim_timer = 0
        self.anim_speed = 10
        self.current_image = self.idle_right

        self.is_jumping = False
        self.jump_anim_timer = 0
        self.jump_anim_length = 10

    def move(self):
        if self.is_dashing:
            return
        
        keys = pygame.key.get_pressed()
        self.velocity_x = 0

        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
            self.facing = "left"
            self.last_facing = "left"
            self.state = "run"
        if keys[pygame.K_d]:
            self.velocity_x = self.speed
            self.facing = "right"
            self.last_facing = "right"
            self.state = "run"
        else:
            if self.on_ground:
                self.state = "idle"
        
    def jump(self):
        if self.jumps_left > 0:
            self.velocity_y = self.jump_power
            self.jumps_left -= 1

            self.is_jumping = True
            self.jump_anim_timer = self.jump_anim_length
        
        elif self.on_left_wall:
            self.velocity_y = self.wall_jump_power_y
            self.velocity_x = self.wall_jump_power_x
            self.facing = "right"

        elif self.on_right_wall:
            self.velocity_y = self.wall_jump_power_y
            self.velocity_x = -self.wall_jump_power_x
            self.facing = "left"
        
        if self.jumps_left == 0:
            self.shadow_burst_left = SHADOW_BURST
            self.shadow_cooldown = 0
        
    def update(self, tiles):
        self.on_left_wall = False
        self.on_right_wall = False

        self.rect.x += self.velocity_x
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.velocity_x > 0:
                    self.rect.right = tile.left
                    self.on_right_wall = True
                if self.velocity_x < 0:
                    self.rect.left = tile.right
                    self.on_left_wall = True
        
        if not self.is_dashing:
            self.velocity_y += self.gravity

        self.rect.y += self.velocity_y
        self.on_ground = False
    
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.velocity_y > 0:
                    self.rect.bottom = tile.top
                    self.velocity_y = 0
                    self.on_ground = True
                    self.jumps_left = self.max_jumps
                    self.is_jumping = False
                    self.state = "idle"
                elif self.velocity_y < 0:
                    self.rect.top = tile.bottom
                    self.velocity_y = 0


        if self.is_dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
                self.dash_cooldown_timer = self.dash_cooldown
        
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= 1

        if self.shadow_burst_left > 0:
            self.shadow_cooldown += 1
            if self.shadow_cooldown >= SHADOW_COOLDOWN:
                self.create_shadows()
                self.shadow_burst_left -= 1
                self.shadow_cooldown = 0

        if self.flash_timer > 0:
            self.flash_timer -= 1
        else:
            self.flash_colour = None

        if self.jump_anim_timer > 0:
            self.jump_anim_timer -= 1
        else:
            self.is_jumping = False
        

        self.update_sprite() 

    def draw_shadows(self, screen, camera):
        for shadow in self.shadows[:]:
            shadow[3] -= 1
            if shadow[3] <= 0:
                self.shadows.remove(shadow)
                continue
                
            alpha = int(255 * (shadow[3] / self.shadow_lifetime))
            image = shadow[2].copy()
            image.set_alpha(alpha)
            screen.blit(image, (shadow[0] - camera.offset_x, shadow[1]  + self.rect.height - image.get_height() - camera.offset_y))
            
    def create_shadows(self):
        self.shadows.append([self.rect.x, self.rect.y, self.current_image.copy(), self.shadow_lifetime])
    
    def dash(self):
        if not self.is_dashing and self.dash_cooldown_timer == 0:
            self.is_dashing = True
            self.dash_timer = self.dash_time

            if self.facing == "right":
                self.velocity_x = self.dash_speed
            else:
                self.velocity_x = -self.dash_speed
        
            self.velocity_y = 0

    def lose_life(self):
        if self.current_health > 0:
            self.current_health -= 1
        
    def update_health_fade(self):
        for i in range(self.max_health):
            if i >= self.current_health:
                self.life_fades[i] = max(0, self.life_fades[i] - self.fade_speed)
            else:
                self.life_fades[i] = 255
    
    def draw_health_bar(self, screen, x, y, boxsize=24, spacing=6):
        for i in range(self.max_health):
            alpha = self.life_fades[i]

            box = pygame.Surface((boxsize, boxsize), pygame.SRCALPHA)
            box.fill((255,0,0, alpha))

            screen.blit(box, (x + i * (boxsize + spacing), y))

            pygame.draw.rect(screen, (255,255,255), (x + i * (boxsize + spacing), y, boxsize, boxsize), 2)

    def update_sprite(self):
        frame = (pygame.time.get_ticks() // 200) % 2

        if self.is_jumping:
            if self.facing == "right":
                self.current_image = self.jumping_right if frame == 0 else self.jumping_right_2
            else:
                self.current_image = self.jumping_left if frame  == 0 else self.jumping_left_2
            return
        
        if self.velocity_x != 0:
            if self.facing == "right":
                self.current_image = self.running_right if frame == 0 else self.idle_right_2
            else:
                self.current_image = self.running_left if frame == 0 else self.idle_left_2
            return

        if self.last_facing == "right":
            self.current_image = self.idle_right if frame == 0 else self.idle_right_2
        else:
            self.current_image = self.idle_left if frame == 0 else self.idle_left_2

    def gain_life(self):
        self.max_health += 1
        self.current_health += 1
        self.life_fades.append(255)
    
    def start_green_flash(self):
        self.flash_timer = 15
        self.flash_colour = (50, 255, 50)

    def respawn(self):
        if self.spawn_points:
            self.rect.topleft = self.spawn_points[0]
        self.velocity_x = 0
        self.velocity_y = 0
        self.jumps_left = self.max_jumps
        self.shadows.clear()
