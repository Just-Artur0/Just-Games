import pygame
from assets import all_player_images, equip_image, unequip_image, back_image, maintheme
from button import Button
from resize import game_surface, render_to_screen, is_fullscreen, toggle_fullscreen, handle_resize
from sys import exit
from menus import mainmenu
import player_selected
def select():
    run = True
    clock = pygame.time.Clock()
    back = Button(200, 100, back_image)
    COLS = 6
    SPACING = 40
    CHAR_SIZE = 100
    buttons = []
    for _ in all_player_images:
        buttons.append({
            "equip": Button(100, 40, equip_image),
            "unequip": Button(100, 40, unequip_image),
            "char_rect": None,
            "btn_pos": None
        })
    x_start = 200
    y_start = 80
    while run:
        clock.tick(10)
        game_surface.fill((0,0,0))
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    exit()
                case pygame.VIDEORESIZE:
                    handle_resize(event.w, event.h)
                case pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE and is_fullscreen:
                        toggle_fullscreen()
                case pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    back_rect = pygame.Rect(0, 0, 200, 100)
                    if back_rect.collidepoint(mx, my):
                        maintheme.stop()
                        return mainmenu()
                    for i, btn in enumerate(buttons):
                        if btn["char_rect"] and btn["char_rect"].collidepoint(mx, my):
                            player_selected.selected_index = i
                        bx, by = buttons[i]["btn_pos"]
                        if bx <= mx <= bx+100 and by <= my <= by+40:
                            if player_selected.selected_index == i:
                                player_selected.selected_index = None   # unequip
                            else:
                                player_selected.selected_index = i       # equip
        for index, img in enumerate(all_player_images):
            row = index // COLS
            col = index % COLS
            x = x_start + col * (CHAR_SIZE + SPACING)
            y = y_start + row * (CHAR_SIZE + 50)
            character = pygame.transform.scale(img, (CHAR_SIZE, CHAR_SIZE))
            rect = game_surface.blit(character, (x, y))
            buttons[index]["char_rect"] = rect
            btn_pos = (x, y + CHAR_SIZE + 10)
            buttons[index]["btn_pos"] = btn_pos
            if player_selected.selected_index == index:
                game_surface.blit(buttons[index]["unequip"].image, buttons[index]["btn_pos"])
            else:
                game_surface.blit(buttons[index]["equip"].image, buttons[index]["btn_pos"])
        game_surface.blit(back.image, (0, 0))
        render_to_screen()