import pygame
from assets import redlight_button_image, dalgona_button_image, tugofwar_button_image, marbles_button_image, justgame_image, freeplay_image, storymode_image, pentathlon_button_image, season3_button_image
from assets import glass_bridge_button_image, squidgame_button_image, mingle_button_image, back_image, maintheme, season1_button_image, season2_button_image, hide_button_image, jumprope_button_image
from assets import playerselect_image, sky_button_image
from resize import handle_resize, toggle_fullscreen, scale_mouse_pos, render_to_screen, game_surface, is_fullscreen
from button import Button
from sys import exit
from redlight import redlight
from dalgona import dalgona
from tugofwar import tugofwar
from marbles import marbles
from glassbridge import glass_bridge
from squidgame import squidgame
from pentathlon import six_legged_pentathlon
from mingle import mingle
from hide import hide
from jumprope import jumprope
from sky import sky
def mainmenu():
    maintheme.play(-1)
    justgame = Button(500, 250, justgame_image)
    freeplay_button = Button(100,100,freeplay_image)
    storymode_button = Button(100,100,storymode_image)
    playerselect_button = Button(100,100,playerselect_image)
    clock = pygame.time.Clock()
    while True:
        clock.tick(10)
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
                    mx, my = scale_mouse_pos(*event.pos)
                    STORYMODE_RECT = pygame.Rect(600, 420, storymode_button.width, storymode_button.height)
                    FREEPLAY_RECT = pygame.Rect(600, 520, freeplay_button.width, freeplay_button.height)
                    PLAYERSELECT_RECT = pygame.Rect(600, 620, playerselect_button.width, playerselect_button.height)
                    if STORYMODE_RECT.collidepoint(mx, my):
                        return storymode_menu(0)
                    elif FREEPLAY_RECT.collidepoint(mx, my):
                        return storymode_menu(1)
                    elif PLAYERSELECT_RECT.collidepoint(mx, my):
                        from player_select import select
                        return select()
        game_surface.fill((0,0,0))
        game_surface.blit(justgame.image, (400, 100))
        game_surface.blit(storymode_button.image, (600, 420))
        game_surface.blit(freeplay_button.image, (600, 520))
        game_surface.blit(playerselect_button.image, (600, 620))
        render_to_screen()
def freeplay_menu(menu=0):
    match menu:
        case 0:
            buttons = [
                Button(200, 100, redlight_button_image),
                Button(200, 100, dalgona_button_image),
                Button(200, 100, tugofwar_button_image),
                Button(200, 100, marbles_button_image),
                Button(200, 100, glass_bridge_button_image),
                Button(200, 100, squidgame_button_image),
                Button(200, 100, back_image)
            ]
            positions = [(200, 150), (450, 150), (700, 150), (200, 300), (450, 300), (700, 300), (0, 0)]
        case 1:
            buttons = [
                Button(200, 100, redlight_button_image),
                Button(200, 100, pentathlon_button_image),
                Button(200, 100, mingle_button_image),
                Button(200, 100, back_image)
            ]
            positions = [(200, 150), (450, 150), (700, 150), (0, 0)]
        case 2:
            buttons = [
                Button(200, 100, hide_button_image),
                Button(200, 100, jumprope_button_image),
                Button(200, 100, sky_button_image),
                Button(200, 100, back_image)
            ]
            positions = [(200, 150), (450, 150), (700, 150), (0, 0)]
    clock = pygame.time.Clock()
    while True:
        clock.tick(10)
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
                    mx, my = scale_mouse_pos(*event.pos)
                    for i, btn in enumerate(buttons):
                        x, y = positions[i]
                        rect = pygame.Rect(x, y, btn.width, btn.height)
                        if rect.collidepoint(mx, my):
                            maintheme.stop()
                            match i:
                                case 0:
                                    match menu:
                                        case 0:
                                            return redlight(1)
                                        case 1:
                                            return redlight(3)
                                        case 2:
                                            return hide(1)
                                case 1:
                                    match menu:
                                        case 0:
                                            return dalgona(1)
                                        case 1:
                                            return six_legged_pentathlon(1)
                                        case 2:
                                            return jumprope(1)
                                case 2:
                                    match menu:
                                        case 0:
                                            return tugofwar(1)
                                        case 1:
                                            return mingle(1)
                                        case 2:
                                            return sky(1)
                                case 3:
                                    match menu:
                                        case 0:
                                            return marbles(1)
                                        case 1:
                                            return mainmenu()
                                        case 2:
                                            return mainmenu()
                                case 4:
                                    return glass_bridge(1)
                                case 5:
                                    return squidgame(1)
                                case 6:
                                    return mainmenu()
        game_surface.fill((0, 0, 0))
        for i, btn in enumerate(buttons):
            x, y = positions[i]
            game_surface.blit(btn.image, (x, y))
        render_to_screen()
def storymode_menu(mode=0):
    buttons = [
        Button(200, 100, season1_button_image),
        Button(200, 100, season2_button_image),
        Button(200, 100, season3_button_image),
        Button(200, 100, back_image)
    ]
    positions = [(440, 150), (440, 300), (440, 450), (0, 0)]
    clock = pygame.time.Clock()
    while True:
        clock.tick(10)
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
                    mx, my = scale_mouse_pos(*event.pos)
                    for i, btn in enumerate(buttons):
                        x, y = positions[i]
                        rect = pygame.Rect(x, y, btn.width, btn.height)
                        if rect.collidepoint(mx, my):
                            match i:
                                case 0:
                                    match mode:
                                        case 0:
                                            maintheme.stop()
                                            from ddakji_story import story_ddakji
                                            return story_ddakji(0)
                                        case 1:
                                            return freeplay_menu(0)
                                case 1:
                                    match mode:
                                        case 0:
                                            maintheme.stop()
                                            from ddakji_story import story_ddakji
                                            return story_ddakji(1)
                                        case 1:
                                            return freeplay_menu(1)
                                case 2:
                                    match mode:
                                        case 0:
                                            maintheme.stop()
                                            from ddakji_story import story_ddakji
                                            return story_ddakji(1)
                                        case 1:
                                            return freeplay_menu(2)
                                case 3:
                                    maintheme.stop()
                                    return mainmenu()
        game_surface.fill((0, 0, 0))
        for i, btn in enumerate(buttons):
            x, y = positions[i]
            game_surface.blit(btn.image, (x, y))
        render_to_screen()