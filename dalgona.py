import pygame
from assets import dalgona_image, background_dalgona_image, dalgona_theme, dalgona_scratch, dalgona_crack, needle_img, shape_images, crack_images
from main import font_path
from player import reset_player
from intro import play_intro_and_show_subtitles
from resize import handle_resize, toggle_fullscreen, is_fullscreen, render_to_screen, game_surface
from random import choice
from time import time, sleep
from sys import exit
def dalgona(freeplay=0):
    reset_player()
    play_intro_and_show_subtitles(2)
    scratch_channel = pygame.mixer.Channel(5)
    crack_channel = pygame.mixer.Channel(4)
    dalgona_theme.play(-1)
    clock = pygame.time.Clock()
    shape_name = choice(list(shape_images.keys()))
    shape_img = shape_images[shape_name]
    dalgona_pos = (
        game_surface.get_width() // 2 - dalgona_image.get_width() // 2,
        game_surface.get_height() // 2 - dalgona_image.get_height() // 2
    )
    shape_pos = (
        dalgona_pos[0] + dalgona_image.get_width() // 2 - shape_img.get_width() // 2,
        dalgona_pos[1] + dalgona_image.get_height() // 2 - shape_img.get_height() // 2
    )
    shape_mask = pygame.mask.from_surface(shape_img)
    grid_cols = 20
    grid_rows = 20
    rect_width = shape_img.get_width() // grid_cols
    rect_height = shape_img.get_height() // grid_rows
    carving_zones = []
    for row in range(grid_rows):
        for col in range(grid_cols):
            rect = pygame.Rect(col * rect_width, row * rect_height, rect_width, rect_height)
            pixels_in_mask = 0
            total_pixels = rect_width * rect_height
            for x in range(rect.left, rect.right):
                for y in range(rect.top, rect.bottom):
                    if shape_mask.get_at((x, y)):
                        pixels_in_mask += 1
            if pixels_in_mask / total_pixels > 0.15:
                carving_zones.append(rect)
    carved = [False] * len(carving_zones)
    font_success = pygame.font.Font(font_path, 55)
    font_lose = pygame.font.Font(font_path, 50)
    success = False
    lost = False
    mouse_held = False
    lives = 4
    last_crack_time = 0
    dalgona_start_time = time()
    DALGONA_DURATION = 180
    target_fps = 60
    while True:
        dalgona_elapsed = time() - dalgona_start_time
        dalgona_time_left = max(0, DALGONA_DURATION - int(dalgona_elapsed))
        game_surface.blit(background_dalgona_image, (0, 0))
        game_surface.blit(dalgona_image, dalgona_pos)
        game_surface.blit(shape_img, shape_pos)
        crack_img = crack_images[4 - lives]
        game_surface.blit(crack_img, dalgona_pos)
        for i, rect in enumerate(carving_zones):
            rect_on_screen = rect.move(shape_pos)
            if carved[i]:
                pygame.draw.rect(game_surface, (0, 255, 0, 150), rect_on_screen)
            else:
                s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                s.fill((255, 0, 0, 100))
                game_surface.blit(s, rect_on_screen.topleft)
                pygame.draw.rect(game_surface, (255, 0, 0), rect_on_screen, 2)
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
                    mouse_held = True
                    target_fps = 30
                case pygame.MOUSEBUTTONUP:
                    scratch_channel.stop()
                    pygame.mouse.set_visible(True)
                    mouse_held = False
                    target_fps = 15
        if mouse_held and not lost and not success:
            if not scratch_channel.get_busy():
                scratch_channel.play(dalgona_scratch, loops=-1)
            mouse_pos = pygame.mouse.get_pos()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            pygame.mouse.set_visible(False)
            game_surface.blit(needle_img, (mouse_x - 6, mouse_y - 393))
            carved_outside = True
            for i, rect in enumerate(carving_zones):
                rect_on_screen = rect.move(shape_pos)
                if rect_on_screen.collidepoint(mouse_pos):
                    carved_outside = False
                    if not carved[i]:
                        carved[i] = True
            if carved_outside and not success:
                current_time = pygame.time.get_ticks()
                if current_time - last_crack_time >= 1000:   #1000 ms = 1 second
                    crack_channel.play(dalgona_crack)
                    lives -= 1
                    last_crack_time = current_time
                    if lives <= 0:
                        lost = True
        if lost:
            from menus import mainmenu
            pygame.mouse.set_visible(True)
            dalgona_theme.stop()
            dalgona_scratch.stop()
            text = font_lose.render("You lost! Carved outside the shape!", True, (255, 0, 0))
            game_surface.blit(text, (game_surface.get_width() // 2 - text.get_width() // 2, 80))
            pygame.display.flip()
            sleep(3)
            return mainmenu()
        elif all(carved) and not lost:
            success = True
        if success:
            pygame.mouse.set_visible(True)
            dalgona_scratch.stop()
            minutes = dalgona_time_left // 60
            seconds = dalgona_time_left % 60
            timer_text = f"{int(minutes):02}:{int(seconds):02}"
            font = pygame.font.Font(font_path, 60)
            timer_surface = font.render(timer_text, True, (255, 0, 0))
            game_surface.blit(timer_surface, (game_surface.get_width() // 2 - timer_surface.get_width() // 2, 20))
            text = font_success.render("Success! Shape Completed!", True, (0, 255, 0))
            game_surface.blit(text, (game_surface.get_width() // 2 - text.get_width() // 2, 80))
            pygame.display.flip()
        if success and dalgona_time_left <= 0:
            dalgona_theme.stop()
            from menus import mainmenu
            if freeplay == 0:
                from lobby import lobby
                lobby("Prepare for Tug of War!", duration=40, lights=1)
                from tugofwar import tugofwar
                return tugofwar(0)
            elif freeplay == 1:
                return mainmenu()
        elif not success and dalgona_time_left <= 0:
            pygame.mouse.set_visible(True)
            dalgona_theme.stop()
            from menus import mainmenu
            return mainmenu()
        # Draw countdown timer
        minutes = dalgona_time_left // 60
        seconds = dalgona_time_left % 60
        timer_text = f"{int(minutes):02}:{int(seconds):02}"
        font = pygame.font.Font(font_path, 60)
        timer_surface = font.render(timer_text, True, (255, 0, 0))
        game_surface.blit(timer_surface, (game_surface.get_width() // 2 - timer_surface.get_width() // 2, 20))
        render_to_screen()
        clock.tick(target_fps)