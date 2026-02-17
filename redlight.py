import pygame
from assets import doll_image, doll_forward_image, background_image, flymetothemoon_sound, flymetothemoon_remix_sound, gunshot_sound, dorm, doll5_sound, doll4_sound, doll3_sound, doll2_sound
from player import player1, all_player_images, reset_player, player_image
from intro import play_intro_and_show_subtitles
from resize import handle_resize, toggle_fullscreen, is_fullscreen, render_to_screen, game_surface
from random import randint, choice
from time import time, sleep
from main import font_path
from doll import Doll
from sys import exit
import player_selected
def redlight(freeplay=0):
    global player_image
    dorm.stop()
    reset_player()
    doll_channel = pygame.mixer.Channel(1)
    flymetothemoon_channel = pygame.mixer.Channel(6)
    play_intro_and_show_subtitles(1)
    if player_selected.selected_index is None:
        if freeplay != 0:
            sprite_id = randint(0, 22)
            player_image = all_player_images[sprite_id]
    else:
        player_image = all_player_images[player_selected.selected_index]
    move_delay = 5000
    doll_sound = doll5_sound
    doll1 = Doll(200, 400, doll_image)
    font = pygame.font.Font(font_path, 60)
    play_doll_sound = False
    play_gunshot = False
    recently_shot = False
    clock = pygame.time.Clock()
    doll_sound.set_volume(0.3)
    doll_channel.play(doll_sound)
    start_time = time()
    last_move_time = pygame.time.get_ticks()
    RLGL_DURATION = 300
    prev_pos = (player1.x, player1.y)
    while True:
        clock.tick(60)
        current_time = pygame.time.get_ticks()
        elapsed_time = time() - start_time
        time_left = max(0, RLGL_DURATION - int(elapsed_time))
        if current_time - last_move_time > move_delay:
            doll1.is_forward = not doll1.is_forward
            move_delay = choice([2000, 3000, 4000, 5000])
            if not doll1.is_forward:
                recently_shot = False
                match move_delay:
                    case 2000:
                        doll_sound = doll2_sound
                    case 3000:
                        doll_sound = doll3_sound
                    case 4000:
                        doll_sound = doll4_sound
                    case 5000:
                        doll_sound = doll5_sound
                play_doll_sound = True
            last_move_time = current_time
        current_pos = player1.x, player1.y
        if doll1.is_forward:
            if current_pos != prev_pos and not recently_shot:
                play_gunshot = True
                recently_shot = True
                player1.x, player1.y = 0, 620
                prev_pos = (player1.x, player1.y)
        if play_doll_sound and not doll_channel.get_busy():
            doll_sound.set_volume(0.3)
            doll_channel.play(doll_sound)
            play_doll_sound = False
        if play_gunshot and not pygame.mixer.Channel(0).get_busy():
            gunshot_sound.play()
            play_gunshot = False
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
        keys = pygame.key.get_pressed()
        can_move = (not doll1.is_forward) or (not recently_shot)
        if can_move:
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player1.x += 1
                if player1.x > 1230:
                    player1.x -= 1
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player1.x -= 1
                if player1.x < 0:
                    player1.x += 1
        prev_pos = current_pos
        doll1.image = doll_forward_image if doll1.is_forward else doll_image
        if time_left <= 0:
            if player1.x >= 1200:
                player1.next_game = True
            else:
                player1.eliminated = True
        if player1.eliminated:
            from menus import mainmenu
            doll_channel.stop()
            lose_text = font.render("You Lost...", True, (255, 0, 0))
            game_surface.blit(lose_text, (game_surface.get_width() // 2 - lose_text.get_width() // 2, 600))
            render_to_screen()
            sleep(3)
            return mainmenu()
        elif player1.next_game:
            from menus import mainmenu
            from lobby import lobby
            doll_channel.stop()
            win_text = font.render("You WON!", True, (0, 255, 0))
            game_surface.blit(win_text, (game_surface.get_width() // 2 - win_text.get_width() // 2, 600))
            render_to_screen()
            sleep(3)
            match freeplay:
                case 0:
                    lobby("Dalgona is up next!", duration=20, lights=0)
                    from dalgona import dalgona
                    return dalgona(0)
                case 1:
                    return mainmenu()
                case 2:
                    lobby("Six Legged Pentathlon is Next!", duration=20, lights=0)
                    from pentathlon import six_legged_pentathlon
                    return six_legged_pentathlon(0)
                case 3:
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
        timer_surface = font.render(timer_text, True, (255, 0, 0))
        game_surface.blit(timer_surface, (game_surface.get_width() // 2 - timer_surface.get_width() // 2, 20))
        game_surface.blit(player_image, (player1.x, player1.y))   #Draw the player on the screen
        render_to_screen()