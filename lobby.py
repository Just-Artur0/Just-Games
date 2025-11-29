import pygame
from main import font_path
from player import Player, player1, player_image
from random import randint, random, choice
from time import time
from math import sin, pi
from sys import exit
from assets import all_player_images, dormitory_image, knife_image, money, dorm
from resize import is_fullscreen, toggle_fullscreen, handle_resize, render_to_screen, game_surface
import player_selected
def lobby(message="Waiting for next game...", duration=20, lights=0):
    global player_image
    if player_selected.selected_index is not None:
        player_image = all_player_images[player_selected.selected_index]
    money.play()
    player1.x = 0
    player1.y = 620
    font2 = pygame.font.Font(font_path, 36)
    small_font = pygame.font.Font(font_path, 24)
    prompt_font = pygame.font.Font(font_path, 40)
    health_font = pygame.font.Font(font_path, 20)
    start_time = time()
    brightness_timer = 0
    brightness_cycle_duration = 120  # frames for full cycle (2 seconds at 60fps)
    min_brightness = 5  # darkest point (0-255)
    max_brightness = 255
    knife_image_right = pygame.transform.rotate(knife_image, -45)
    knife_image_left = pygame.transform.rotate(knife_image, 45)
    knife_swing_frames = 50
    swing_counter = 0
    swing_phase_delay = 25
    last_key_pressed = None
    has_attacked = False
    player1.health = 100
    bot = Player(0, 620)  # start position for bot
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
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)
        now = time()
        elapsed = now - start_time
        time_left1 = max(0, duration - int(elapsed))
        if lights == 1:
            brightness_timer += 1
            # Create sine wave oscillation for smooth brightness transition
            brightness_factor = (sin(brightness_timer * 2 * pi / brightness_cycle_duration) + 1) / 2
            current_brightness = int(min_brightness + (max_brightness - min_brightness) * brightness_factor)
            # Create a surface for the brightness overlay
            brightness_surface = pygame.Surface(game_surface.get_size())
            brightness_surface.set_alpha(255 - current_brightness)
            brightness_surface.fill((0, 0, 0))  # Black overlay
        game_surface.blit(dormitory_image, (0, 0))
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
        if keys[pygame.K_RIGHT]:
            last_key_pressed = "right"
            player1.x += 3
            if player1.x > game_surface.get_width() - 50:
                player1.x -= 3
        elif keys[pygame.K_LEFT]:
            last_key_pressed = "left"
            player1.x -= 3
            if player1.x < 0:
                player1.x += 3
        if lights == 1:
            if keys[pygame.K_SPACE] and last_key_pressed is not None and swing_counter == 0:
                player1.knife_active = True
                has_attacked = True
                player1.knife_direction = last_key_pressed
                swing_counter = knife_swing_frames
            else:
                if swing_counter <= 0:
                    player1.knife_active = False
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
                    bot_move_direction = choice(["left", "right", "idle"])
                    bot_move_timer = randint(30, 60)
                # Move bot
                if bot_move_direction == "left":
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
            if bot.health > 0:
                game_surface.blit(bot2_image, (bot.x, bot.y))
                health_text = health_font.render(f"{int(bot.health)} HP", True, (255, 0, 0))
                game_surface.blit(health_text, (bot.x, bot.y - 20))
            game_surface.blit(player_image, (player1.x, player1.y))  # Draw the player on the window
            health_text = health_font.render(f"{int(player1.health)} HP", True, (255, 0, 0))
            game_surface.blit(health_text, (player1.x, player1.y - 20))
            if not has_attacked:
                prompt_text = prompt_font.render("Press SPACE to Attack", True, (255, 255, 255))
                game_surface.blit(prompt_text, (game_surface.get_width() // 2 - prompt_text.get_width() // 2, 60))
            game_surface.blit(brightness_surface, (0, 0))
        msg = font2.render(message, True, (255, 255, 255))
        game_surface.blit(msg, (game_surface.get_width() // 2 - msg.get_width() // 2, 150))
        minutes = time_left1 // 60
        seconds = time_left1 % 60
        timer_text = f"Next Game in {int(minutes):02}:{int(seconds):02}"
        timer_surface = small_font.render(timer_text, True, (255, 0, 0))
        game_surface.blit(timer_surface, (game_surface.get_width() // 2 - timer_surface.get_width() // 2, 20))
        game_surface.blit(player_image, (player1.x, player1.y))
        render_to_screen()
        if time_left1 <= 0:
            money.stop()
            break
def waiting(story=0):
    dorm.play(-1)
    waiting_font = pygame.font.Font(font_path, 60)
    COUNTDOWN_DURATION = 30
    start_time = time()
    clock = pygame.time.Clock()
    while True:
        clock.tick(5)
        elapsed_time = time() - start_time
        countdown_remaining = max(0, COUNTDOWN_DURATION - int(elapsed_time))
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
        game_surface.blit(dormitory_image, (0, 0))
        if countdown_remaining <= 0 and story == 0:
            from redlight import redlight
            return redlight(0)
        elif countdown_remaining <= 0 and story == 1:
            from redlight import redlight
            return redlight(2)
        countdown_text = f"Starting in: {countdown_remaining} seconds"
        countdown_render = waiting_font.render(countdown_text, True, (255, 215, 0))
        game_surface.blit(countdown_render, (game_surface.get_width()//2 - countdown_render.get_width()//2, game_surface.get_height()//2 + 40))
        render_to_screen()