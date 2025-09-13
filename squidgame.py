import pygame
from assets import background_squidgame_image, knife_image, squidgame_voiceline1, squidgame_voiceline2, squidgame_voiceline3, rain_theme, finalist_suit_image
from player import player_image, all_player_images, player1, reset_player
from resize import handle_resize, toggle_fullscreen, is_fullscreen, render_to_screen, window, game_surface
from intro import play_intro_and_show_subtitles
from os.path import join
from sys import exit
from random import choice, randint, random
from time import sleep, time
from player import Player
def squidgame(freeplay=0):
    global player_image, window, is_fullscreen
    pygame.font.init()
    reset_player()
    play_intro_and_show_subtitles(6)
    if freeplay == 1:
        sprite_id = randint(0, 22)
        player_image = all_player_images[sprite_id]
    font_path = join("Fonts", "Game Of Squids.ttf")
    knife_image_right = pygame.transform.rotate(knife_image, -45)
    knife_image_left = pygame.transform.rotate(knife_image, 45)
    knife_swing_frames = 50
    swing_counter = 0
    swing_phase_delay = 25
    clock = pygame.time.Clock()
    font = pygame.font.Font(font_path, 60)
    player1.x = 0
    player1.y = 620
    player1.health = 100
    bot = Player(600, 400)  # start position for bot
    bot.health = 100
    bot.knife_active = False
    bot.knife_direction = "left"
    bot.hit_player_id = None
    bot.eliminated = False
    bot2_sprite_id = randint(0, 22)
    bot2_image = all_player_images[bot2_sprite_id]
    bot_move_timer = 0
    bot_attack_timer = 0
    bot_swing_counter = 0
    bot_move_direction = choice(["up", "down", "left", "right"])
    last_key_pressed = None
    has_attacked = False
    rain_theme_played = False
    rain_drops = []
    for _ in range(50):  # number of drops
        x = randint(0, game_surface.get_width())
        y = randint(0, game_surface.get_height())
        speed = randint(4, 10)
        rain_drops.append([x, y, speed])
    subtitle_start_time = time()
    subtitle_events = [
        (20, 4, ("Good rain knows the best time to fall.", ""), squidgame_voiceline1),
        (60, 2, ("Remember this place?", "이곳을 기억하시나요?"), squidgame_voiceline2),
        (62, 3, ("We played Red Light, Green Light here.", "우리는 여기서 레드 라이트, 그린 라이트를 연주했습니다."), None),
        (65, 3, ("They're all dead. Everyone who was here back then,", "다 죽었어. 그때 여기 있던 사람들은 다 죽었어."), None),
        (68, 4, ("except for you and me.", "당신과 나를 제외하고."), None),
        (74, 2, ("We've...", "우리는..."), None),
        (76, 4, ("come too far to go back.", "돌아갈 수 없을 만큼 멀리 왔다."), None),
        (120, 2, ("When we were kids,", "우리가 어렸을 때,"), squidgame_voiceline3),
        (122, 3, ("we would play just like this,", "우리는 이렇게 플레이할 거야,"), None),
        (127, 3, ("and our moms would call us in for dinner.", "그리고 우리 엄마들은 우리를 저녁 식사에 부르곤 했습니다."), None),
        (132, 4, ("But no one calls us anymore.", "하지만 더 이상 우리에게 전화를 걸어오는 사람은 없습니다."), None),
    ]
    font_korean = pygame.font.SysFont("malgungothic", 34)
    font_english = pygame.font.SysFont("Arial", 30)
    rain_theme_channel = pygame.mixer.Channel(7)
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.VIDEORESIZE:
                handle_resize(event.w, event.h)
                rain_drops = []
                for _ in range(50):  # number of drops
                    x = randint(0, game_surface.get_width())
                    y = randint(0, game_surface.get_height())
                    speed = randint(4, 10)
                    rain_drops.append([x, y, speed])
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    toggle_fullscreen()
                    rain_drops = []
                    for _ in range(50):  # number of drops
                        x = randint(0, game_surface.get_width())
                        y = randint(0, game_surface.get_height())
                        speed = randint(4, 10)
                        rain_drops.append([x, y, speed])
                elif event.key == pygame.K_ESCAPE and is_fullscreen:
                    toggle_fullscreen()
                    rain_drops = []
                    for _ in range(50):  # number of drops
                        x = randint(0, game_surface.get_width())
                        y = randint(0, game_surface.get_height())
                        speed = randint(4, 10)
                        rain_drops.append([x, y, speed])
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            last_key_pressed = "right"
            player1.x += 3
            if player1.x > 1230:
                player1.x -= 3
        elif keys[pygame.K_LEFT]:
            last_key_pressed = "left"
            player1.x -= 3
            if player1.x < 0:
                player1.x += 3
        if keys[pygame.K_UP]:
            player1.y -= 3
            if player1.y < 0:
                player1.y += 3
        elif keys[pygame.K_DOWN]:
            player1.y += 3
            if player1.y > 620:
                player1.y -= 3
        if keys[pygame.K_SPACE] and last_key_pressed is not None and swing_counter == 0:
            player1.knife_active = True
            has_attacked = True
            player1.knife_direction = last_key_pressed
            swing_counter = knife_swing_frames
        else:
            if swing_counter <= 0:
                player1.knife_active = False
        game_surface.blit(background_squidgame_image, (0, 0))
        if swing_counter > 0:
            phase = knife_swing_frames - swing_counter
            # Phase 0 → show normal knife (wind-up)
            if phase < swing_phase_delay:
                if player1.knife_direction == "right":
                    game_surface.blit(knife_image, (player1.x + 50, player1.y))
                else:
                    game_surface.blit(knife_image, (player1.x - 20, player1.y))
            # Phase 1 → show tilted knife (attack frame)
            else:
                if player1.knife_direction == "right":
                    knife_img = knife_image_right
                    knife_offset = (player1.x + 40, player1.y)
                else:
                    knife_img = knife_image_left
                    knife_offset = (player1.x - 65, player1.y)
                knife_rect = knife_img.get_rect(topleft=knife_offset)
                game_surface.blit(knife_img, knife_offset)
            # Damage check only after swing_phase_delay
            if phase >= swing_phase_delay:
                bot_rect = pygame.Rect(bot.x, bot.y, player_image.get_width(), player_image.get_height())
                if knife_rect.colliderect(bot_rect):
                    bot.health -= 1
                    if bot.health <= 0:
                        bot.eliminated = True
            swing_counter -= 1
        else:
            player1.knife_active = False
        if not bot.eliminated:
            bot_move_timer -= 1
            bot_attack_timer -= 1
            # Change direction every ~1 second
            if bot_move_timer <= 0:
                bot_move_direction = choice(["up", "down", "left", "right", "idle"])
                bot_move_timer = randint(30, 60)
            # Move bot
            if bot_move_direction == "up":
                bot.y -= 3
            elif bot_move_direction == "down":
                bot.y += 3
            elif bot_move_direction == "left":
                bot.x -= 3
                bot.knife_direction = "left"
            elif bot_move_direction == "right":
                bot.x += 3
                bot.knife_direction = "right"
            # Keep inside bounds
            bot.x = max(0, min(1230, bot.x))
            bot.y = max(0, min(620, bot.y))
            # Random attack every 2–4 seconds
            if bot_attack_timer <= 0 and bot_swing_counter == 0:
                if random() < 0.02:  # small chance per frame
                    bot.knife_active = True
                    bot_swing_counter = knife_swing_frames
                    bot_attack_timer = randint(120, 240)
            # Handle bot knife swing
            if bot_swing_counter > 0:
                phase = knife_swing_frames - bot_swing_counter
                # Phase 0 → show normal knife (wind-up)
                if phase < swing_phase_delay:
                    if bot.knife_direction == "right":
                        game_surface.blit(knife_image, (bot.x + 50, bot.y))
                    else:
                        game_surface.blit(knife_image, (bot.x - 20, bot.y))
                # Phase 1 → show tilted knife (attack frame)
                else:
                    if bot.knife_direction == "right":
                        knife_img = knife_image_right
                        knife_offset = (bot.x + 40, bot.y)
                    else:
                        knife_img = knife_image_left
                        knife_offset = (bot.x - 65, bot.y)
                    knife_rect = knife_img.get_rect(topleft=knife_offset)
                    game_surface.blit(knife_img, knife_offset)
                    # Player hit detection
                    player_rect = pygame.Rect(
                        player1.x, player1.y,
                        player_image.get_width(),
                        player_image.get_height()
                    )
                    if knife_rect.colliderect(player_rect):
                        player1.health -= 1
                        if player1.health <= 0:
                            player1.eliminated = True
                bot_swing_counter -= 1
            else:
                bot.knife_active = False
        # Draw bot
        game_surface.blit(bot2_image, (bot.x, bot.y))
        game_surface.blit(finalist_suit_image, (bot.x, bot.y + 41))
        health_font = pygame.font.Font(font_path, 20)
        health_text = health_font.render(f"{int(bot.health)} HP", True, (255, 0, 0))
        game_surface.blit(health_text, (bot.x, bot.y - 20))
        game_surface.blit(player_image, (player1.x, player1.y))  # Draw the player on the window
        game_surface.blit(finalist_suit_image, (player1.x, player1.y + 41))
        health_font = pygame.font.Font(font_path, 20)
        health_text = health_font.render(f"{int(player1.health)} HP", True, (255, 0, 0))
        game_surface.blit(health_text, (player1.x, player1.y - 20))
        if not has_attacked:
            prompt_font = pygame.font.Font(font_path, 40)
            prompt_text = prompt_font.render("Press SPACE to Attack", True, (255, 255, 255))
            game_surface.blit(prompt_text, (game_surface.get_width() // 2 - prompt_text.get_width() // 2, 10))
        elapsed = time() - subtitle_start_time
        if elapsed >= 20:
            if not rain_theme_played:
                rain_theme.set_volume(0.4)
                rain_theme_channel.play(rain_theme, -1)
                rain_theme_played = True
            for drop in rain_drops:
                drop[1] += drop[2]  # Move down
                # If the drop goes off-screen, reset to top
                if drop[1] > 720:
                    drop[0] = randint(0, 1280)  # random X
                    drop[1] = randint(-20, -5)  # above screen
                    drop[2] = randint(4, 10)    # speed
                # Draw the drop
                pygame.draw.line(game_surface, (173, 216, 230), (drop[0], drop[1]), (drop[0], drop[1] + 5), 1)  # light blue thin line
        current_english = ""
        current_korean = ""
        for start_t, duration, (eng, kor), sound_obj in subtitle_events:
            if start_t <= elapsed <= start_t + duration:
                current_english = eng
                current_korean = kor
                # Play sound if available and not already playing
                if sound_obj and not pygame.mixer.Channel(0).get_busy():
                    pygame.mixer.Channel(0).play(sound_obj)
                break
        # Draw subtitle
        if current_english:
            eng_surface = font_english.render(current_english, True, (255, 0, 0))
            kor_surface = font_korean.render(current_korean, True, (255, 255, 255))
            game_surface.blit(kor_surface, (game_surface.get_width()//2 - kor_surface.get_width()//2, 600))
            game_surface.blit(eng_surface, (game_surface.get_width()//2 - eng_surface.get_width()//2, 640))
        if player1.eliminated:
            from menus import mainmenu
            lose_text = font.render("You Lost...", True, (255, 0, 0))
            game_surface.blit(lose_text, (game_surface.get_width() // 2 - lose_text.get_width() // 2, 600))
            pygame.display.flip()
            sleep(3)
            rain_theme.stop()
            return mainmenu()
        elif bot.eliminated:
            from menus import mainmenu
            win_text = font.render("You WON!", True, (0, 255, 0))
            game_surface.blit(win_text, (game_surface.get_width() // 2 - win_text.get_width() // 2, 600))
            pygame.display.flip()
            sleep(3)
            rain_theme.stop()
            play_intro_and_show_subtitles(7)
            return mainmenu()
        render_to_screen()