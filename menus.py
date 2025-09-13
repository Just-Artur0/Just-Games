import pygame
from assets import redlight_button_image, dalgona_button_image, tugofwar_button_image, marbles_button_image, justgame_image, freeplay_image, storymode_image, pentathlon_button_image
from assets import glass_bridge_button_image, squidgame_button_image, mingle_button_image, back_image, maintheme, doll_sound, season1_button_image, season2_button_image
from resize import handle_resize, toggle_fullscreen, scale_mouse_pos, render_to_screen, game_surface, window, is_fullscreen
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
def mainmenu():
    global window, is_fullscreen
    doll_sound.stop()
    maintheme.play(-1)
    justgame = Button(500, 250, justgame_image)
    freeplay_button = Button(100,100,freeplay_image)
    storymode_button = Button(100,100,storymode_image)
    clock = pygame.time.Clock()
    while True:
        clock.tick(10)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.VIDEORESIZE:
                handle_resize(event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE and is_fullscreen:
                    toggle_fullscreen()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = scale_mouse_pos(*event.pos)
                STORYMODE_RECT = pygame.Rect(600, 420, storymode_button.width, storymode_button.height)
                FREEPLAY_RECT = pygame.Rect(600, 520, freeplay_button.width, freeplay_button.height)
                if STORYMODE_RECT.collidepoint(mx, my):
                    return storymode_menu(0)
                elif FREEPLAY_RECT.collidepoint(mx, my):
                    return storymode_menu(1)
        game_surface.fill((0,0,0))
        game_surface.blit(justgame.image, (400, 100))
        game_surface.blit(storymode_button.image, (600, 420))
        game_surface.blit(freeplay_button.image, (600, 520))
        render_to_screen()
def freeplay_menu(menu=0):
    global window, is_fullscreen
    if menu == 0:
        buttons = [
            Button(200, 100, redlight_button_image),
            Button(200, 100, dalgona_button_image),
            Button(200, 100, tugofwar_button_image),
            Button(200, 100, marbles_button_image),
            Button(200, 100, glass_bridge_button_image),
            Button(200, 100, squidgame_button_image),
            Button(200, 100, back_image)
        ]
        positions = [
            (200, 150), (450, 150), (700, 150),
            (200, 300), (450, 300), (700, 300), (0, 0)
        ]
    elif menu == 1:
        buttons = [
            Button(200, 100, redlight_button_image),
            Button(200, 100, pentathlon_button_image),
            Button(200, 100, mingle_button_image),
            Button(200, 100, back_image)
        ]
        positions = [
            (200, 150), (450, 150), (700, 150), (0, 0)
        ]
    clock = pygame.time.Clock()
    while True:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.VIDEORESIZE:
                handle_resize(event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE and is_fullscreen:
                    toggle_fullscreen()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = scale_mouse_pos(*event.pos)
                for i, btn in enumerate(buttons):
                    x, y = positions[i]
                    rect = pygame.Rect(x, y, btn.width, btn.height)
                    if rect.collidepoint(mx, my):
                        #print(f"Clicked Freeplay Button {i + 1}")
                        if i == 0:
                            if menu == 0:
                                maintheme.stop()
                                return redlight(1)
                            elif menu == 1:
                                maintheme.stop()
                                return redlight(3)
                        elif i == 1:
                            if menu == 0:
                                maintheme.stop()
                                return dalgona(1)
                            elif menu == 1:
                                maintheme.stop()
                                return six_legged_pentathlon(1)
                        elif i == 2:
                            if menu == 0:
                                maintheme.stop()
                                return tugofwar(1)
                            elif menu == 1:
                                maintheme.stop()
                                return mingle(1)
                        elif i == 3:
                            if menu == 0:
                                maintheme.stop()
                                return marbles(1)
                            elif menu == 1:
                                maintheme.stop()
                                return mainmenu()
                        elif i == 4:
                            maintheme.stop()
                            return glass_bridge(1)
                        elif i == 5:
                            maintheme.stop()
                            return squidgame(1)
                        elif i == 6:
                            maintheme.stop()
                            return mainmenu()
        game_surface.fill((0, 0, 0))
        for i, btn in enumerate(buttons):
            x, y = positions[i]
            game_surface.blit(btn.image, (x, y))
        render_to_screen()
def storymode_menu(mode=0):
    global window, is_fullscreen
    buttons = [
        Button(200, 100, season1_button_image),
        Button(200, 100, season2_button_image),
        Button(200, 100, back_image)
    ]
    positions = [
        (440, 150), (440, 300), (0, 0)
    ]
    clock = pygame.time.Clock()
    while True:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.VIDEORESIZE:
                handle_resize(event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE and is_fullscreen:
                    toggle_fullscreen()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = scale_mouse_pos(*event.pos)
                for i, btn in enumerate(buttons):
                    x, y = positions[i]
                    rect = pygame.Rect(x, y, btn.width, btn.height)
                    if rect.collidepoint(mx, my):
                        #print(f"Clicked Freeplay Button {i + 1}")
                        if i == 0:
                            from ddakji_story import story_ddakji
                            if mode == 0:
                                maintheme.stop()
                                return story_ddakji(0)
                            elif mode == 1:
                                return freeplay_menu(0)
                        elif i == 1:
                            from ddakji_story import story_ddakji
                            if mode == 0:
                                maintheme.stop()
                                return story_ddakji(1)
                            elif mode == 1:
                                return freeplay_menu(1)
                        elif i == 2:
                            maintheme.stop()
                            return mainmenu()
        game_surface.fill((0, 0, 0))
        for i, btn in enumerate(buttons):
            x, y = positions[i]
            game_surface.blit(btn.image, (x, y))
        render_to_screen()