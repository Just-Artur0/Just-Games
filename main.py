import pygame
from os.path import join
pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.display.init()
font_path = join("Fonts", "Game Of Squids.ttf")
if __name__ == "__main__":
    from menus import mainmenu
    mainmenu()