import pygame
from assets import tugofwar_theme, background_tugofwar_image, all_player_images
from player import player1, reset_player, player_image
from intro import play_intro_and_show_subtitles
from resize import handle_resize, toggle_fullscreen, is_fullscreen, render_to_screen, window, scale_mouse_pos, game_surface
from random import choice, randint
from os.path import join
from sys import exit
from time import sleep
def tugofwar(freeplay=0):
    global player_image, window, is_fullscreen
    pygame.font.init()
    reset_player()
    play_intro_and_show_subtitles(3)
    if freeplay == 1:
        sprite_id = randint(0, 22)
        player_image = all_player_images[sprite_id]
    tugofwar_theme.play(-1)
    font_path = join("Fonts", "Game Of Squids.ttf")
    clock = pygame.time.Clock()
    player1.team = choice(['left', 'right'])
    bot_team = 'right' if player1.team == 'left' else 'left'
    last_bot_click = pygame.time.get_ticks()
    bot_click_interval = 450
    bot_sprite_id = randint(0, 22)
    bot_image = all_player_images[bot_sprite_id]
    font = pygame.font.Font(font_path, 60)
    font4 = pygame.font.Font(font_path, 60)
    tug_clicks = {'left': 0, 'right': 0}
    button_color = (0, 200, 0)
    button_hover_color = (0, 255, 0)
    button_rect = pygame.Rect(540, 300, 200, 100)
    click_count = 0
    win_threshold = 300
    while True:
        clock.tick(15)
        game_surface.blit(background_tugofwar_image, (0, 0))
        # Draw Tug Button
        mx, my = scale_mouse_pos(*pygame.mouse.get_pos())
        if button_rect.collidepoint((mx, my)):
            color = button_hover_color
        else:
            color = button_color
        pygame.draw.rect(game_surface, color, button_rect)
        text = font4.render("TUG!", True, (0, 0, 0))
        game_surface.blit(text, (button_rect.x + 15, button_rect.y + 15))
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
                if button_rect.collidepoint(pygame.mouse.get_pos()):
                    click_count += 1
                    tug_clicks[player1.team] += 1
        current_time = pygame.time.get_ticks()
        if current_time - last_bot_click >= bot_click_interval:
            tug_clicks[bot_team] += 1
            last_bot_click = current_time
        bot_x = 200 if bot_team == 'left' else 1000
        game_surface.blit(bot_image, (bot_x, 320))
        pos_xp = 200 if player1.team == 'left' else 1000
        game_surface.blit(player_image, (pos_xp, 320))
        color = (0, 128, 255) if player1.team == 'left' else (255, 50, 50)
        team_text = font.render(f"Team: {player1.team.upper()}", True, color)
        game_surface.blit(team_text, (0, 0))
        if tug_clicks[player1.team] >= win_threshold:
            player1.tug_won = True
        elif tug_clicks['left'] >= win_threshold or tug_clicks['right'] >= win_threshold:
            player1.eliminated = True
        left_score = tug_clicks.get('left', 0)
        right_score = tug_clicks.get('right', 0)
        game_surface.blit(font.render(f"Left: {left_score}/{win_threshold}", True, (0, 0, 255)), (100, 100))
        game_surface.blit(font.render(f"Right: {right_score}/{win_threshold}", True, (255, 0, 0)), (800, 100))
        if player1.tug_won:
            tugofwar_theme.stop()
            win_text = font.render("TEAM WINS!", True, (0, 255, 0))
            game_surface.blit(win_text, (game_surface.get_width() // 2 - win_text.get_width() // 2, 600))
            render_to_screen()
            sleep(3)
            if freeplay == 0:
                from lobby import lobby
                lobby("Marbles is Next!", duration=20, lights=0)
                from marbles import marbles
                return marbles(0)
            elif freeplay == 1:
                from menus import mainmenu
                return mainmenu()
        elif player1.eliminated:
            tugofwar_theme.stop()
            lose_text = font.render("Your Team Lost", True, (255, 0, 0))
            game_surface.blit(lose_text, (game_surface.get_width() // 2 - lose_text.get_width() // 2, 600))
            render_to_screen()
            sleep(3)
            from menus import mainmenu
            return mainmenu()

        render_to_screen()
