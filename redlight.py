import pygame
from assets import doll_image, doll_forward_image, background_image, doll_sound, flymetothemoon_sound, flymetothemoon_remix_sound, gunshot_sound, dorm
from player import player1, all_player_images, reset_player, player_image
from intro import play_intro_and_show_subtitles
from resize import handle_resize, toggle_fullscreen, is_fullscreen, render_to_screen, window, game_surface
from random import randint
from time import time
from os.path import join
from doll import Doll
from sys import exit
def redlight(freeplay=0):
    global player_image, window, is_fullscreen
    dorm.stop()
    pygame.font.init()
    reset_player()
    font_path = join("Fonts", "Game Of Squids.ttf")
    doll_channel = pygame.mixer.Channel(1)
    flymetothemoon_channel = pygame.mixer.Channel(6)
    play_intro_and_show_subtitles(1)
    if freeplay == 1:
        sprite_id = randint(0, 22)
        player_image = all_player_images[sprite_id]
    elif freeplay == 3:
        sprite_id = randint(0, 22)
        player_image = all_player_images[sprite_id]
    move_delay = 5000
    doll1 = Doll(200, 400, doll_image)
    play_doll_sound = False
    clock = pygame.time.Clock()
    doll_sound.set_volume(0.3)
    doll_channel.play(doll_sound)
    start_time = time()
    last_move_time = pygame.time.get_ticks()
    RLGL_DURATION = 300
    while True:
        clock.tick(60)
        current_time = pygame.time.get_ticks()
        elapsed_time = time() - start_time
        time_left = max(0, RLGL_DURATION - int(elapsed_time))
        if current_time - last_move_time > move_delay:
            prev_pos = prev_pos = player1.x, player1.y
            doll1.is_forward = not doll1.is_forward
            if not doll1.is_forward:
                play_doll_sound = False
            if doll1.is_forward:
                play_doll_sound = True
            last_move_time = current_time
        current_pos = player1.x, player1.y
        if doll1.is_forward:
            if current_pos != prev_pos:
                gunshot_sound.play()
                player1.x, player1.y = 0, 620
        if play_doll_sound:
            doll_sound.set_volume(0.3)
            doll_channel.play(doll_sound)
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
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            player1.x += 1
            if player1.x > 1230:
                player1.x -= 1
        if keys[pygame.K_LEFT]:
            player1.x -= 1
            if player1.x < 0:
                player1.x += 1
        doll1.image = doll_forward_image if doll1.is_forward else doll_image
        if time_left <= 0:
            if player1.x >= 1200:
                player1.next_game = True
            else:
                player1.eliminated = True
        if player1.eliminated:
            from menus import mainmenu
            return mainmenu()
        elif player1.next_game:
            from menus import mainmenu
            from lobby import lobby
            if freeplay == 0:
                lobby("Dalgona is up next!", duration=20, lights=0)
                from dalgona import dalgona
                return dalgona(0)
            elif freeplay == 1:
                return mainmenu()
            elif freeplay == 2:
                lobby("Six Legged Pentathlon is Next!", duration=20, lights=0)
                from pentathlon import six_legged_pentathlon
                return six_legged_pentathlon(0)
            elif freeplay == 3:
                return mainmenu()
        game_surface.blit(background_image, (0, 0))
        game_surface.blit(doll1.image, (1080, 315))
        if time_left == 182 and freeplay == 0 or time_left == 182 and freeplay == 1:
            flymetothemoon_channel.play(flymetothemoon_sound)
        elif time_left == 135 and freeplay == 2 or time_left == 135 and freeplay == 3:
            flymetothemoon_channel.play(flymetothemoon_remix_sound)
        # Draw countdown timer
        minutes = time_left // 60
        seconds = time_left % 60
        timer_text = f"{int(minutes):02}:{int(seconds):02}"
        font = pygame.font.Font(font_path, 60)
        timer_surface = font.render(timer_text, True, (255, 0, 0))
        game_surface.blit(timer_surface, (game_surface.get_width() // 2 - timer_surface.get_width() // 2, 20))
        game_surface.blit(player_image, (player1.x, player1.y))   #Draw the player on the screen
        render_to_screen()