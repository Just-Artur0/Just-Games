import pygame
from random import randint
from math import sin
from time import time, sleep
from assets import all_player_images, start_station_image, gun_fire_image, walking_image, ddakji_station_image, blue_ddakji_image, red_ddakji_image
from assets import flying_stone_station_image, stone_image, stone_throw_image, gonggi_station_image, red_circle_gonggi_image, green_triangle_gonggi_image
from assets import blue_circle_gonggi_image, purple_square_gonggi_image, yellow_triangle_gonggi_image, spinning_top_station_image, spinning_top_image, jegi_station_image, jegi_image
from assets import pentathlon_theme, pentathlon_champion_theme, gonggi_pass_image, stone_pass_image, spinningtop_fail_image, pass_sound, spinningtop_pass_image
from assets import one_two_sound, gun_shot_sound, fail_sound, pentathlon_victory, pentathlon_win_image, pass_image, fail_image, jegi_fail_image, ddakji_pass_image, stone_fail_image
from player import player1, player_image, sprite_id, reset_player
from main import font_path
from sys import exit
from intro import play_intro_and_show_subtitles 
from resize import handle_resize, toggle_fullscreen, is_fullscreen, render_to_screen, game_surface, scale_mouse_pos
import player_selected
def six_legged_pentathlon(freeplay=0):
    global sprite_id, player_image
    reset_player()
    play_intro_and_show_subtitles(8)
    if player_selected.selected_index is None:
        if freeplay == 1:
            sprite_id = randint(0, 22)
            player_image = all_player_images[sprite_id]
    else:
        player_image = all_player_images[player_selected.selected_index]
    clock = pygame.time.Clock()
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BAR_WIDTH = 40
    BAR_HEIGHT = 300
    BAR_X = 920
    BAR_Y = 300
    font1 = pygame.font.Font(font_path, 60)
    font2 = pygame.font.Font(font_path, 40)
    instruction_font = pygame.font.Font(font_path, 24)
    power_level = 0
    max_power = 100
    power_speed = 2
    space_held = False
    ddakji_processed = False
    stone_processed = False
    gonggi_processed = False
    spinning_processed = False
    jegi_processed = False
    ddakji_phase = False
    stone_phase = False
    gonggi_phase = False
    spinning_phase = False
    jegi_phase = False
    flip_timer_start = None
    stone_timer_start = None
    gonggi_timer_start = None
    spinning_timer_start = None
    jegi_timer_start = None
    victory_timer_start = None
    throw_start_time = None
    throw_duration = 0.9
    gonggi_level = 1
    num_of_gonggi = 0
    rounds_to_complete = 4
    gonggi_state = "waiting"
    airborne_stone = None
    picked_stones = []
    tossed_stone_start_time = None
    toss_duration = 2.5
    pass_fail_start = None
    pass_fail_state = None
    pre_result_start = None
    pre_result_state = None
    curve_points = []
    green_rect = None
    jegi_rect = None
    blue_ddakji_image1 = pygame.transform.scale(blue_ddakji_image, (100, 100))
    red_ddakji_image1 = pygame.transform.scale(red_ddakji_image, (100, 100))
    stone_throw_image1 = pygame.transform.scale(stone_throw_image, (119, 70))
    red_circle_gonggi_image1 = pygame.transform.scale(red_circle_gonggi_image, (30, 30))
    green_triangle_gonggi_image1 = pygame.transform.scale(green_triangle_gonggi_image, (30, 30))
    blue_circle_gonggi_image1 = pygame.transform.scale(blue_circle_gonggi_image, (30, 30))
    purple_square_gonggi_image1 = pygame.transform.scale(purple_square_gonggi_image, (30, 30))
    yellow_triangle_gonggi_image1 = pygame.transform.scale(yellow_triangle_gonggi_image, (30, 30))
    level1_gonggi = [
        {"image": red_circle_gonggi_image1, "x": 720, "y": 600, "vy": 0, "airborne": False},
        {"image": blue_circle_gonggi_image1, "x": 780, "y": 600, "vy": 0, "airborne": False},
        {"image": purple_square_gonggi_image1, "x": 810, "y": 600, "vy": 0, "airborne": False},
        {"image": green_triangle_gonggi_image1, "x": 750, "y": 600, "vy": 0, "airborne": False},
        {"image": yellow_triangle_gonggi_image1, "x": 840, "y": 600, "vy": 0, "airborne": False},
    ]
    level2_gonggi = [
        {"image": red_circle_gonggi_image1, "x": 700, "y": 600, "vy": 0, "airborne": False},
        {"image": blue_circle_gonggi_image1, "x": 740, "y": 600, "vy": 0, "airborne": False},
        {"image": purple_square_gonggi_image1, "x": 780, "y": 600, "vy": 0, "airborne": False},
        {"image": green_triangle_gonggi_image1, "x": 820, "y": 600, "vy": 0, "airborne": False},
        {"image": yellow_triangle_gonggi_image1, "x": 860, "y": 600, "vy": 0, "airborne": False},
    ]
    level3_gonggi = [
        {"image": red_circle_gonggi_image1, "x": 680, "y": 600, "vy": 0, "airborne": False},
        {"image": blue_circle_gonggi_image1, "x": 730, "y": 600, "vy": 0, "airborne": False},
        {"image": purple_square_gonggi_image1, "x": 780, "y": 600, "vy": 0, "airborne": False},
        {"image": green_triangle_gonggi_image1, "x": 830, "y": 600, "vy": 0, "airborne": False},
        {"image": yellow_triangle_gonggi_image1, "x": 880, "y": 600, "vy": 0, "airborne": False},
    ]
    level4_gonggi = [
        {"image": red_circle_gonggi_image1, "x": 680, "y": 600, "vy": 0, "airborne": False},
        {"image": blue_circle_gonggi_image1, "x": 730, "y": 600, "vy": 0, "airborne": False},
        {"image": purple_square_gonggi_image1, "x": 780, "y": 600, "vy": 0, "airborne": False},
        {"image": green_triangle_gonggi_image1, "x": 830, "y": 600, "vy": 0, "airborne": False},
        {"image": yellow_triangle_gonggi_image1, "x": 880, "y": 600, "vy": 0, "airborne": False},
    ]
    level5_gonggi = [
        {"image": red_circle_gonggi_image1, "x": 680, "y": 200, "vy": -8, "airborne": True},
        {"image": blue_circle_gonggi_image1, "x": 730, "y": 200, "vy": -8, "airborne": True},
        {"image": purple_square_gonggi_image1, "x": 780, "y": 200, "vy": -8, "airborne": True},
        {"image": green_triangle_gonggi_image1, "x": 830, "y": 200, "vy": -8, "airborne": True},
        {"image": yellow_triangle_gonggi_image1, "x": 880, "y": 200, "vy": -8, "airborne": True},
    ]
    current_gonggi = level1_gonggi
    jegix = 440
    jegiy = -1200
    jegi_counter = 0
    pentathlon_champion_theme.set_volume(0.6)
    pentathlon_channel = pygame.mixer.Channel(2)
    fail_pass_sound_played = False
    one_two_sound_played = False
    gun_shot_played = False
    stone_pos = (620, 500) # top-left where the stone sits
    thrower_pos = (650, 300)
    frozen_curve = None # list of curve points when SPACE pressed
    stone_thrown = False
    class BotPlayer:
        def __init__(self, sprite_id, x, y):
            self.sprite_id = sprite_id
            self.x = x
            self.y = y
    bot_players = [
        BotPlayer(randint(0, 22), 0, 0),
        BotPlayer(randint(0, 22), 0, 0), 
        BotPlayer(randint(0, 22), 0, 0),
        BotPlayer(randint(0, 22), 0, 0)
    ]
    match sprite_id: 
        case 1:
            PENTATHLON_DURATION = 311
        case 12:
            PENTATHLON_DURATION = 311
        case 13:
            PENTATHLON_DURATION = 311
        case 14:
            PENTATHLON_DURATION = 311
        case 19:
            PENTATHLON_DURATION = 311
        case _:
            PENTATHLON_DURATION = 308
    match player_selected.selected_index: 
        case 1:
            PENTATHLON_DURATION = 311
        case 12:
            PENTATHLON_DURATION = 311
        case 13:
            PENTATHLON_DURATION = 311
        case 14:
            PENTATHLON_DURATION = 311
        case 19:
            PENTATHLON_DURATION = 311
        case _:
            PENTATHLON_DURATION = 308
    if PENTATHLON_DURATION == 311:
        pentathlon_channel.play(pentathlon_champion_theme, -1)
    else:
        pentathlon_channel.play(pentathlon_theme, -1)
    pentathlon_time_left = PENTATHLON_DURATION
    pentathlon_start_time = time()
    while True:
        clock.tick(25)
        game_surface.blit(start_station_image, (0, 0))
        elapsed = time() - pentathlon_start_time
        pentathlon_time_left = max(-10, PENTATHLON_DURATION - int(elapsed))
        if pentathlon_time_left > 303:
            game_surface.blit(start_station_image, (0 ,0))
            player1.x = 1040
            player1.y = 300
            sprite1 = pygame.transform.scale(player_image, (200, 500))
            game_surface.blit(sprite1, (player1.x, player1.y))
            stations = [
                (740, 200, (200, 700)),
                (500, 200, (200, 700)),
                (250, 200, (200, 700)),
                (0, 200, (200, 700))
            ]
            for i, bot in enumerate(bot_players):
                bot.x, bot.y, scale = stations[i]
                sprite = pygame.transform.scale(all_player_images[bot.sprite_id], scale)
                game_surface.blit(sprite, (bot.x, bot.y))
        elif pentathlon_time_left > 302:
            game_surface.blit(gun_fire_image, (0 ,0))
            if not gun_shot_played:
                gun_shot_sound.play()
                gun_shot_played = True
        elif pentathlon_time_left > 291:
            game_surface.blit(walking_image, (0 ,0))
            if not pygame.mixer.Channel(0).get_busy() and not one_two_sound_played:
                pygame.mixer.Channel(0).play(one_two_sound)
                one_two_sound_played = True
            player1.x = 940
            player1.y = 200
            sprite1 = pygame.transform.scale(player_image, (200, 600))
            game_surface.blit(sprite1, (player1.x, player1.y))
            bot_x_positions = [790, 640, 490, 240]
            for i, bot in enumerate(bot_players):
                bot.x = bot_x_positions[i]
                bot.y = 200
                sprite = pygame.transform.scale(all_player_images[bot.sprite_id], (200, 600))
                game_surface.blit(sprite, (bot.x, bot.y))
        elif pentathlon_time_left <= 291 and not ddakji_processed:
            game_surface.blit(ddakji_station_image, (0 ,0))
            ddakji_phase = True
            player1.x = 640
            player1.y = 280
            sprite1 = pygame.transform.scale(player_image, (200, 300))
            game_surface.blit(sprite1, (player1.x, player1.y))
            bot_positions = [
                (440, 100, (200, 500)),
                (340, 100, (200, 500)), 
                (240, 140, (200, 500)),
                (140, 160, (200, 500))
            ]
            for i, bot in enumerate(bot_players):
                bot.x, bot.y, scale = bot_positions[i]
                sprite = pygame.transform.scale(all_player_images[bot.sprite_id], scale)
                game_surface.blit(sprite, (bot.x, bot.y))
            fill_height = int((power_level / max_power) * BAR_HEIGHT)
            pygame.draw.rect(game_surface, WHITE, (BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT), 2)
            if fill_height > 0:
                pygame.draw.rect(game_surface, RED, (BAR_X, BAR_Y + BAR_HEIGHT - fill_height, BAR_WIDTH, fill_height))
            if player1.pentathlon_ddakji_flipped:
                # Show flipped ddakji image
                game_surface.blit(red_ddakji_image1, (620, 500))
                game_surface.blit(blue_ddakji_image1, (620, 430))
            else:
                game_surface.blit(red_ddakji_image1, (620, 500))
                game_surface.blit(blue_ddakji_image1, (620, 100))
            space_surface = font2.render("Hold Space to fill Strength Bar", True, (255, 0, 0))
            game_surface.blit(space_surface, (game_surface.get_width()//2 - space_surface.get_width()//2, 660))
        elif flip_timer_start is not None and not stone_processed:
            game_surface.blit(walking_image, (0, 0))
            if not pygame.mixer.Channel(0).get_busy() and not one_two_sound_played:
                pygame.mixer.Channel(0).play(one_two_sound)
                one_two_sound_played = True
            player1.x = 940
            player1.y = 200
            sprite1 = pygame.transform.scale(player_image, (200, 600))
            game_surface.blit(sprite1, (player1.x, player1.y))
            bot_x_positions = [790, 640, 490, 240]
            for i, bot in enumerate(bot_players):
                bot.x = bot_x_positions[i]
                bot.y = 200
                sprite = pygame.transform.scale(all_player_images[bot.sprite_id], (200, 600))
                game_surface.blit(sprite, (bot.x, bot.y))
            if time() - flip_timer_start >= 10:
                game_surface.blit(flying_stone_station_image, (0, 0))
                stone_phase = True
                one_two_sound.stop()
                player1.x = 590
                player1.y = 100
                sprite1 = pygame.transform.scale(player_image, (200, 500))
                game_surface.blit(sprite1, (player1.x, player1.y))
                bot_positions = [
                    (790, 100, (200, 500)),
                    (490, 100, (200, 500)),
                    (390, 100, (200, 500)),
                    (240, 100, (200, 500))
                ]
                for i, bot in enumerate(bot_players):
                    bot.x, bot.y, scale = bot_positions[i]
                    sprite = pygame.transform.scale(all_player_images[bot.sprite_id], scale)
                    game_surface.blit(sprite, (bot.x, bot.y))
                game_surface.blit(stone_image, stone_pos)
                space_surface = font2.render("Press Space to Throw Stone", True, (255, 0, 0))
                game_surface.blit(space_surface, (game_surface.get_width()//2 - space_surface.get_width()//2, 660))
                if not stone_thrown:
                    game_surface.blit(stone_throw_image1, thrower_pos)
                # Build curve from center of thrower -> center of stone
                thrower_rect = stone_throw_image1.get_rect(topleft=thrower_pos)
                stone_rect   = stone_image.get_rect(topleft=stone_pos)
                start_x, start_y = thrower_rect.centerx, thrower_rect.centery
                end_x,   end_y   = stone_rect.centerx,   stone_rect.centery
                num_points = 42
                wiggle = sin(time() * 2) * 500  # swing amplitude
                # If not frozen, build moving curve
                if frozen_curve is None:
                    curve_points = []
                    for i in range(num_points):
                        t = i / (num_points - 1)
                        bx = start_x + (end_x - start_x) * t
                        by = start_y + (end_y - start_y) * t
                        x = bx + wiggle * t
                        y = by
                        curve_points.append((x, y))
                        if i % 2 == 0:
                            pygame.draw.circle(game_surface, WHITE, (int(x), int(y)), 4)
                else:
                    # draw frozen dotted curve
                    for i, (x, y) in enumerate(frozen_curve):
                        if i % 2 == 0:
                            pygame.draw.circle(game_surface, WHITE, (int(x), int(y)), 4)
                # If throw started, animate along frozen curve
                if throw_start_time is not None:
                    stone_thrown = True
                    progress = (time() - throw_start_time) / throw_duration
                    progress = max(0.0, min(1.0, progress))
                    idx = int(progress * (num_points - 1))
                    if frozen_curve:
                        x, y = frozen_curve[idx]
                        proj_rect = stone_throw_image1.get_rect(center=(int(x), int(y)))
                        game_surface.blit(stone_throw_image1, proj_rect.topleft)
                        # At end of throw, check collision
                        if progress >= 1.0:
                            if proj_rect.colliderect(stone_rect):
                                player1.stone_hit = True
                            else:
                                throw_start_time = None
                                frozen_curve = None
                                stone_thrown = False
                                pre_result_state = "fail"
                                pre_result_start = time()
                                pentathlon_channel.pause()
        elif stone_timer_start is not None and not gonggi_processed:
            game_surface.blit(walking_image, (0, 0))
            if not pygame.mixer.Channel(0).get_busy() and not one_two_sound_played:
                pygame.mixer.Channel(0).play(one_two_sound)
                one_two_sound_played = True
            player1.x = 940
            player1.y = 200
            sprite1 = pygame.transform.scale(player_image, (200, 600))
            game_surface.blit(sprite1, (player1.x, player1.y))
            bot_x_positions = [790, 640, 490, 240]
            for i, bot in enumerate(bot_players):
                bot.x = bot_x_positions[i]
                bot.y = 200
                sprite = pygame.transform.scale(all_player_images[bot.sprite_id], (200, 600))
                game_surface.blit(sprite, (bot.x, bot.y))
            if time() - stone_timer_start >= 10:
                game_surface.blit(gonggi_station_image, (0, 0))
                gonggi_phase = True
                one_two_sound.stop()
                player1.x = 553
                player1.y = 33
                sprite1 = pygame.transform.scale(player_image, (260, 532))
                game_surface.blit(sprite1, (player1.x, player1.y))
                bot_positions = [
                    (8, 57, (282, 663)),
                    (290, 75, (263, 596)),
                    (813, 82, (237, 482)),
                    (1050, 143, (186, 511))
                ]
                for i, bot in enumerate(bot_players):
                    bot.x, bot.y, scale = bot_positions[i]
                    sprite = pygame.transform.scale(all_player_images[bot.sprite_id], scale)
                    game_surface.blit(sprite, (bot.x, bot.y))
                # Choose which gonggi set to use based on level
                match gonggi_level: 
                    case 1:
                        current_gonggi = level1_gonggi
                    case 2:
                        current_gonggi = level2_gonggi
                    case 3:
                        current_gonggi = level3_gonggi
                    case 4:
                        current_gonggi = level4_gonggi
                    case 5:
                        current_gonggi = level5_gonggi
                for gonggi in current_gonggi:
                    # Create rect for collision detection
                    gonggi["rect"] = pygame.Rect(gonggi["x"], gonggi["y"], 30, 30)
                    # Draw the stone
                    game_surface.blit(gonggi["image"], (gonggi["x"], gonggi["y"]))
                    # Gravity for airborne stone
                    if gonggi.get("airborne", False):
                        gonggi["vy"] += 1.5  # gravity
                        gonggi["y"] += gonggi["vy"]
                        # Check if stone landed
                        if gonggi["y"] >= 600:
                            gonggi["y"] = 600
                            gonggi["airborne"] = False
                            gonggi["vy"] = 0
                # Display level information
                level_text = f"Level {gonggi_level} - Progress: {num_of_gonggi}/{rounds_to_complete}"
                level_surface = instruction_font.render(level_text, True, (0, 0, 255))
                game_surface.blit(level_surface, (500, 150))
                match gonggi_state: 
                    case "waiting":
                        match gonggi_level:
                            case 1:
                                instruction = "Level 1: Click a stone to toss it up"
                            case 2:
                                instruction = "Level 2: Click a stone to toss it up"
                            case 3:
                                instruction = "Level 3: Click a stone to toss it up"
                            case 4:
                                instruction = "Level 4: Click a stone to toss it up"
                            case 5:
                                instruction = "Level 5: Press Space To Catch"
                        instruction_surface = instruction_font.render(instruction, True, (255, 0, 0))
                        game_surface.blit(instruction_surface, (500, 200))
                    case "stone_in_air":
                        time_left = toss_duration - (time() - tossed_stone_start_time)
                        if gonggi_level == 5:
                            time_left = 1.5 - (time() - tossed_stone_start_time)
                        if time_left > 0:
                            match gonggi_level: 
                                case 1:
                                    instruction = f"Pick up ONE stone! Time: {time_left:.1f}s"
                                case 2:
                                    instruction = f"Pick up TWO stones! Time: {time_left:.1f}s"
                                case 3:
                                    instruction = f"Pick up THREE stones! Time: {time_left:.1f}s"
                                case 4:
                                    instruction = f"Pick up FOUR stones! Time: {time_left:.1f}s"
                                case 5:
                                    instruction = f"Time: {time_left:.1f}s"
                            instruction_surface = instruction_font.render(instruction, True, (0, 255, 0))
                            game_surface.blit(instruction_surface, (500, 200))
                            if time_left <= 0:
                                if gonggi_level == 5 and not player1.gonggi_caught:
                                    num_of_gonggi = 0
                                    gonggi_state = "stone_in_air"  # Level 5 starts with stones in air
                                    tossed_stone_start_time = time()
                                    for stone in level5_gonggi:
                                        stone["y"] = 200
                                        stone["airborne"] = True
                                        stone["vy"] = 0 
                                if airborne_stone:
                                    airborne_stone["vy"] = 0
                                    airborne_stone["airborne"] = True
                                    gonggi_state = "catching"
                        else:
                            gonggi_state = "catching"
                    case "catching":
                        instruction = "Waiting..."
                        instruction_surface = instruction_font.render(instruction, True, (255, 255, 0))
                        game_surface.blit(instruction_surface, (500, 200))
                        # Check if airborne stone landed
                        if airborne_stone and not airborne_stone.get("airborne", False):
                            # Check success/failure based on level
                            match gonggi_level: 
                                case 1:
                                    stones_needed = 1
                                    rounds_to_complete = 4  # Level 1: need 4 rounds of picking 1 stone each
                                case 2:
                                    stones_needed = 2
                                    rounds_to_complete = 2  # Level 2: need 2 rounds of picking 2 stones each
                                case 3:
                                    # Level 3 special logic: Round 1 = pick 3, Round 2 = pick 1
                                    if num_of_gonggi == 0:
                                        stones_needed = 3  # First round: pick 3 stones
                                    else:
                                        stones_needed = 1  # Second round: pick 1 stone
                                    rounds_to_complete = 2  # Level 3: 2 rounds total (3+1)
                                case 4:
                                    stones_needed = 4
                                    rounds_to_complete = 1
                                case 5:
                                    stones_needed = 5
                                    rounds_to_complete = 1
                            if len(picked_stones) == stones_needed:
                                # SUCCESS! 
                                num_of_gonggi += 1
                                if num_of_gonggi >= rounds_to_complete:  # Use proper completion requirement
                                    match gonggi_level: 
                                        case 1:
                                            # Move to Level 2
                                            gonggi_level = 2
                                            num_of_gonggi = 0  # Reset progress for Level 2
                                            gonggi_state = "waiting"
                                            # Reset all stones to ground for Level 2
                                            for stone in level2_gonggi:
                                                stone["y"] = 600
                                                stone["airborne"] = False
                                                stone["vy"] = 0
                                        case 2:
                                            # Move to Level 3
                                            gonggi_level = 3
                                            num_of_gonggi = 0
                                            gonggi_state = "waiting"
                                            for stone in level3_gonggi:
                                                stone["y"] = 600
                                                stone["airborne"] = False
                                                stone["vy"] = 0
                                        case 3:
                                            gonggi_level = 4
                                            num_of_gonggi = 0
                                            gonggi_state = "waiting"
                                            for stone in level4_gonggi:
                                                stone["y"] = 600
                                                stone["airborne"] = False
                                                stone["vy"] = 0
                                        case 4:
                                            gonggi_level = 5
                                            num_of_gonggi = 0
                                            gonggi_state = "stone_in_air"  # Level 5 starts with stones in air
                                            tossed_stone_start_time = time()
                                            # All stones start airborne in Level 5
                                            for stone in level5_gonggi:
                                                stone["y"] = 200
                                                stone["airborne"] = True
                                                stone["vy"] = 0
                                else:
                                    gonggi_state = "waiting"  # Continue current level
                            else:
                                # FAILURE - didn't pick correct number of stones
                                if gonggi_level != 5:
                                    pass_fail_state = "fail"
                                    pass_fail_start = time()
                                    pentathlon_channel.pause()
                                    fail_sound.play()
                                    gonggi_state = "waiting"
                                    num_of_gonggi = 0
                                    for stone in current_gonggi:
                                        stone["y"] = 600
                                        stone["airborne"] = False
                                        stone["vy"] = 0
                                elif gonggi_level == 5:
                                    num_of_gonggi = 0
                                    gonggi_state = "stone_in_air"  # Level 5 starts with stones in air
                                    tossed_stone_start_time = time()
                                    for stone in level5_gonggi:
                                        stone["y"] = 200
                                        stone["airborne"] = True
                                        stone["vy"] = 0 
                            # Reset for next round
                            if gonggi_level != 5:
                                airborne_stone = None
                                picked_stones = []
                                tossed_stone_start_time = None
        elif gonggi_timer_start is not None and not spinning_processed:
            game_surface.blit(walking_image, (0, 0))
            if not pygame.mixer.Channel(0).get_busy() and not one_two_sound_played:
                pygame.mixer.Channel(0).play(one_two_sound)
                one_two_sound_played = True
            player1.x = 940
            player1.y = 200
            sprite1 = pygame.transform.scale(player_image, (200, 600))
            game_surface.blit(sprite1, (player1.x, player1.y))
            bot_x_positions = [790, 640, 490, 240]
            for i, bot in enumerate(bot_players):
                bot.x = bot_x_positions[i]
                bot.y = 200
                sprite = pygame.transform.scale(all_player_images[bot.sprite_id], (200, 600))
                game_surface.blit(sprite, (bot.x, bot.y))
            if time() - gonggi_timer_start >= 10:
                game_surface.blit(spinning_top_station_image, (0, 0))
                spinning_phase = True
                one_two_sound.stop()
                player1.x = 397
                player1.y = 106
                sprite1 = pygame.transform.scale(player_image, (236, 614))
                game_surface.blit(sprite1, (player1.x, player1.y))
                bot_positions = [
                    (892, 215, (88, 505)),
                    (799, 135, (93, 585)),
                    (633, 77, (166, 643)),
                    (245, 84, (152, 636))
                ]
                for i, bot in enumerate(bot_players):
                    bot.x, bot.y, scale = bot_positions[i]
                    sprite = pygame.transform.scale(all_player_images[bot.sprite_id], scale)
                    game_surface.blit(sprite, (bot.x, bot.y))
                fill_height = int((power_level / max_power) * BAR_HEIGHT)
                game_surface.blit(spinning_top_image, (440, 260))
                pygame.draw.rect(game_surface, WHITE, (BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT), 2)
                if fill_height > 0:
                    pygame.draw.rect(game_surface, RED, (BAR_X, BAR_Y + BAR_HEIGHT - fill_height, BAR_WIDTH, fill_height))
                space_surface = font2.render("Hold Space to fill Strength Bar", True, (255, 0, 0))
                game_surface.blit(space_surface, (game_surface.get_width()//2 - space_surface.get_width()//2, 660))
        elif spinning_timer_start is not None and not jegi_processed:
            game_surface.blit(walking_image, (0, 0))
            if not pygame.mixer.Channel(0).get_busy() and not one_two_sound_played:
                pygame.mixer.Channel(0).play(one_two_sound)
                one_two_sound_played = True
            player1.x = 940
            player1.y = 200
            sprite1 = pygame.transform.scale(player_image, (200, 600))
            game_surface.blit(sprite1, (player1.x, player1.y))
            bot_x_positions = [790, 640, 490, 240]
            for i, bot in enumerate(bot_players):
                bot.x = bot_x_positions[i]
                bot.y = 200
                sprite = pygame.transform.scale(all_player_images[bot.sprite_id], (200, 600))
                game_surface.blit(sprite, (bot.x, bot.y))
            if time() - spinning_timer_start >= 10:
                game_surface.blit(jegi_station_image, (0, 0))
                jegi_phase = True
                one_two_sound.stop()
                game_surface.blit(jegi_image, (jegix, jegiy))
                pygame.draw.line(game_surface, (0, 255, 0), (550, 400), (650, 400), 5)
                pygame.draw.line(game_surface, RED, (550, 600), (650, 600), 5)
                green_rect = pygame.Rect(550, 400 - 5 // 2, 100, 5)
                red_rect = pygame.Rect(550, 600 - 5 // 2, 100, 5)
                jegi_rect = pygame.Rect(jegix + 135, jegiy + 255, 65, 48)
                jegiy += 32
                if red_rect.colliderect(jegi_rect):
                    jegiy = -3000
                    jegi_counter = 0
                    pre_result_state = "fail"
                    pre_result_start = time()
                    pentathlon_channel.pause()
                space_surface = font2.render("Press Space on the Green Line", True, (255, 0, 0))
                game_surface.blit(font1.render(f"{int(jegi_counter)}/5", True, (255, 0, 0)), (840, 320))
                game_surface.blit(space_surface, (game_surface.get_width()//2 - space_surface.get_width()//2, 660))
                if jegi_counter >= 5:
                    player1.jegi_pass = True
        elif jegi_timer_start is not None and jegi_processed:
            game_surface.blit(walking_image, (0, 0))
            if not pygame.mixer.Channel(0).get_busy() and not one_two_sound_played:
                pygame.mixer.Channel(0).play(one_two_sound)
                one_two_sound_played = True
            player1.x = 940
            player1.y = 200
            sprite1 = pygame.transform.scale(player_image, (200, 600))
            game_surface.blit(sprite1, (player1.x, player1.y))
            bot_x_positions = [790, 640, 490, 240]
            for i, bot in enumerate(bot_players):
                bot.x = bot_x_positions[i]
                bot.y = 200
                sprite = pygame.transform.scale(all_player_images[bot.sprite_id], (200, 600))
                game_surface.blit(sprite, (bot.x, bot.y))
            if time() - jegi_timer_start >= 10:
                game_surface.blit(pentathlon_win_image, (0, 0))
                one_two_sound.stop()
                pentathlon_champion_theme.stop()
                pentathlon_theme.stop()
                if not fail_pass_sound_played:
                    pentathlon_victory.play()
                    victory_timer_start = time()
                    fail_pass_sound_played = True
                player1.pentathlon_win = True
        if victory_timer_start is not None:
            if time() - victory_timer_start >= 23:
                win_text = font1.render("Your Team Won!", True, (255, 0, 0))
                game_surface.blit(win_text, (game_surface.get_width() // 2 - win_text.get_width() // 2, 600))
                render_to_screen()
                sleep(3)
                match freeplay: 
                    case 1:
                        from menus import mainmenu
                        return mainmenu()
                    case 0:
                        from lobby import lobby
                        lobby("Get Ready for Mingle!", 20, 0)
                        from mingle import mingle
                        return mingle(0)
        for event in pygame.event.get():
            match event.type: 
                case pygame.QUIT:
                    exit()
                case pygame.VIDEORESIZE:
                    handle_resize(event.w, event.h)
                case pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not ddakji_processed and ddakji_phase:
                        space_held = True
                    elif event.key == pygame.K_SPACE and not spinning_processed and spinning_phase:
                        space_held = True
                    elif event.key == pygame.K_F11:
                        toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE and is_fullscreen:
                        toggle_fullscreen()
                case pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        if not ddakji_processed and ddakji_phase:
                            space_held = False
                            if power_level >= 70 and power_level <= 80:
                                player1.pentathlon_ddakji_flipped = True
                            else:
                                pass_fail_state = "fail"
                                pass_fail_start = time()
                                pentathlon_channel.pause()
                                fail_sound.play()
                            # Reset power after action
                            power_level = 0
                        elif not spinning_processed and spinning_phase:
                            space_held = False
                            if power_level >= 50 and power_level <= 60:
                                player1.spinning = True
                            else:
                                pre_result_state = "fail"
                                pre_result_start = time()
                                pentathlon_channel.pause()
                            # Reset power after action
                            power_level = 0
            if event.type == pygame.MOUSEBUTTONDOWN and not gonggi_processed and gonggi_phase:
                mx, my = scale_mouse_pos(*event.pos)
                match gonggi_state: 
                    case "waiting":
                        # Click to toss a stone
                        for gonggi in current_gonggi:
                            if gonggi["rect"].collidepoint(mx, my) and gonggi["y"] == 600:
                                # Toss this stone up
                                gonggi["y"] = 200  # Start high
                                gonggi["vy"] = -16   # Upward velocity
                                gonggi["airborne"] = True
                                airborne_stone = gonggi
                                tossed_stone_start_time = time()
                                gonggi_state = "stone_in_air"         
                    case "stone_in_air":
                        # Click to pick up stones from ground
                        for gonggi in current_gonggi:
                            if (gonggi["rect"].collidepoint(mx, my) and 
                                gonggi["y"] == 600 and 
                                gonggi != airborne_stone and
                                gonggi not in picked_stones):
                                # Pick up this stone
                                picked_stones.append(gonggi)
                                gonggi["y"] = 550  # Lift slightly to show it's picked
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and gonggi_level == 5 and gonggi_state == 'stone_in_air' and not gonggi_processed and gonggi_phase:
            player1.gonggi_caught = True
        elif keys[pygame.K_SPACE] and not jegi_processed and jegi_phase and green_rect is not None and jegi_rect is not None:
            if green_rect.colliderect(jegi_rect):
                jegiy = -400
                jegi_counter += 1
        elif keys[pygame.K_SPACE] and not stone_processed and stone_phase:
            # trigger throw only once
            if throw_start_time is None:
                frozen_curve = curve_points.copy()
                throw_start_time = time()
        elif space_held:
            power_level = min(max_power, power_level + power_speed)
        if player1.jegi_pass:
            if jegi_timer_start is None:
                pass_fail_state = "pass"
                pass_fail_start = time()
                pentathlon_channel.unpause()
                pass_sound.play()
                jegi_phase = False
                jegi_processed = True
                jegi_timer_start = time()
        elif player1.spinning:
            if spinning_timer_start is None:
                pre_result_state = "pass"
                pre_result_start = time()
                pentathlon_channel.unpause()
                spinning_phase = False
                spinning_processed = True
                spinning_timer_start = time()
        elif player1.gonggi_caught:
            if gonggi_timer_start is None:
                pre_result_state = "pass"
                pre_result_start = time()
                pentathlon_channel.unpause()
                gonggi_phase = False
                gonggi_processed = True
                gonggi_timer_start = time()
        elif player1.stone_hit:
            if stone_timer_start is None:
                pre_result_state = "pass"
                pre_result_start = time()
                pentathlon_channel.unpause()
                stone_phase = False
                stone_processed = True
                stone_timer_start = time()
        elif player1.pentathlon_ddakji_flipped:
            if flip_timer_start is None:
                ddakji_phase = False
                ddakji_processed = True
                pre_result_state = "pass"
                pre_result_start = time()
                pentathlon_channel.unpause()
                flip_timer_start = time()
        if pre_result_state is not None and pre_result_start is not None:
            shown_for = time() - pre_result_start
            if shown_for < 1.5:
                if pre_result_state == "pass":
                    if spinning_processed:
                        game_surface.blit(spinningtop_pass_image, (0, 0))
                    elif gonggi_processed:
                        game_surface.blit(gonggi_pass_image, (0, 0))
                    elif stone_processed:
                        game_surface.blit(stone_pass_image, (0, 0))
                    elif ddakji_processed:
                        game_surface.blit(ddakji_pass_image, (0, 0))
                if pre_result_state == "fail":
                    if not stone_processed:
                        game_surface.blit(stone_fail_image, (0, 0))
                    elif not spinning_processed:
                        game_surface.blit(spinningtop_fail_image, (0, 0))
                    elif not jegi_processed:
                        game_surface.blit(jegi_fail_image, (0, 0))
            else:
                # Transition to pass/fail after 1.5 seconds
                pass_fail_state = pre_result_state
                pass_fail_start = time()
                pre_result_state = None
                pre_result_start = None
        elif pass_fail_state is not None and pass_fail_start is not None:
            shown_for = time() - pass_fail_start
            if shown_for < 2:
                if pass_fail_state == "pass":
                    game_surface.blit(pass_image, (0, 0))
                    if not fail_pass_sound_played:
                        pass_sound.play()
                        fail_pass_sound_played = True
                elif pass_fail_state == "fail":
                    game_surface.blit(fail_image, (0, 0))
                    if not fail_pass_sound_played:
                        fail_sound.play()
                        fail_pass_sound_played = True
            else:
                # Reset after 2 seconds
                one_two_sound_played = False
                fail_pass_sound_played = False
                pass_fail_state = None
                pass_fail_start = None
        if pentathlon_time_left <= 0 and victory_timer_start is None:
            pentathlon_champion_theme.stop()
            pentathlon_theme.stop()
            lose_text = font1.render("You Lost...", True, (255, 0, 0))
            game_surface.blit(lose_text, (game_surface.get_width() // 2 - lose_text.get_width() // 2, 600))
            render_to_screen()
            sleep(3)
            player1.voted = False
            from menus import mainmenu
            return mainmenu()
        # Draw countdown timer
        if pentathlon_time_left <= 0:
            minutes = 0
            seconds = 0
        elif pentathlon_time_left <= 300:
            minutes = pentathlon_time_left // 60
            seconds = pentathlon_time_left % 60
        else:
            minutes = 5
            seconds = 0
        timer_text = f"{int(minutes):02}:{int(seconds):02}"
        timer_surface = font1.render(timer_text, True, (255, 0, 0))
        game_surface.blit(timer_surface, (game_surface.get_width() // 2 - timer_surface.get_width() // 2, 20))
        render_to_screen()