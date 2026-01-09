import pygame

def draw_death_flash(screen, alpha):
    if alpha <= 0:
        return
    
    flash = pygame.Surface(screen.get_size())
    flash.fill((255,0,0))
    flash.set_alpha(alpha)
    screen.blit(flash, (0,0))
