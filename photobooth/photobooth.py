import os
import pygame
import pygame_menu

pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'
surface = pygame.display.set_mode((600, 400))

menu = pygame_menu.Menu(height=300,
                        width=400,
                        theme=pygame_menu.themes.THEME_BLUE,
                        title='Welcome')