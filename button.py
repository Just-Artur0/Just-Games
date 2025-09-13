import pygame
from resize import game_surface, window
class Button:
    def __init__(self, width, height, image):
        self.width = width
        self.height = height
        self.image = image
        self.image = pygame.transform.scale(image, (self.width, self.height))
def draw_button(rect, text, font, color=(255, 255, 255), bg_color=(50, 50, 50)):
    pygame.draw.rect(window, bg_color, rect, border_radius=10)
    label = font.render(text, True, color)
    label_rect = label.get_rect(center=rect.center)
    game_surface.blit(label, label_rect)