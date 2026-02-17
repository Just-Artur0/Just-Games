import pygame
from main import font_path
from assets import key_image, hide_knife_image, door_image, hide_background_image, stairs_image, red_image, blue_image, hide_theme, unlock, o_patch_image
from intro import play_intro_and_show_subtitles
from player import player_image, all_player_images, player1, reset_player, Player
from resize import handle_resize, toggle_fullscreen, is_fullscreen, render_to_screen, game_surface
from sys import exit
from random import choice, randint, random
from time import sleep, time
import player_selected
def hide(freeplay=0):
    global player_image
    reset_player()
    if player_selected.selected_index is None:
        if freeplay == 1:
            sprite_id = randint(0, 22)
            player_image = all_player_images[sprite_id]
    else:
        player_image = all_player_images[player_selected.selected_index]
    play_intro_and_show_subtitles(14)
    hide_theme_channel = pygame.mixer.Channel(6)
    clock = pygame.time.Clock()
    floor1 = ["                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
              "B                                                                                                      B",
              "B                                                                                                      B",
              "# S                                                                                                S   #",
              "#           L               L              L               L                L            L             #",
              "#                                                                                                      #",
              "########################################################################################################",]
    floor2 = ["                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
              "B                                                                                                      B",
              "B                                                                                                      B",
              "# S                                                                                                S   #",
              "#           L               L              L               L                L            L             #",
              "#                                                                                                      #",
              "########################################################################################################",]
    floor3 = ["                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "                                                                                                        ",
              "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB",
              "B                                                                                                      B",
              "B                                                                                                      B",
              "# S                                                                                                S   #",
              "#           L               L              L               L                L            L             #",
              "#                                                                                                      #",
              "########################################################################################################",]
    room1 = ["####################",
             "#                  #",
             "#                  #",
             "#                  #",
             "#                 L#",
             "#                  #",
             "####################",]
    floors = {1: floor1, 2: floor2, 3: floor3}
    current_floor = 1
    TILE_SIZE = 50
    available_keys = ["square", "triangle", "circle", "star"]#
    team = choice(["blue", "red"])
    bot_team = None
    match team:
        case "red":
            bot_team = "blue"
            player_keys = ["None"]
        case "blue":
            bot_team = "red"
            player_keys = [choice(available_keys)]  # e.g., ["square", "triangle"]
    # Door-key mapping (door rect -> key type)
    door_keys = {}
    platforms = []
    doors = []
    stairs = []
    floor_states = {}
    class Door:
        def __init__(self, rect, key_type):
            self.rect = rect
            self.key_type = key_type
            self.opened = False
    def setup_floor(floor_num): 
        platforms = [] 
        stairs = [] 
        doors = [] 
        if floor_num in floor_states:
            doors = floor_states[floor_num]
            level = floors[floor_num]
            for row_index, row in enumerate(level): 
                for col_index, tile in enumerate(row): 
                    x = col_index * TILE_SIZE 
                    y = row_index * TILE_SIZE 
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE) 
                    match tile:
                        case "#": 
                            platforms.append(rect) 
                        case "S": 
                            stairs.append(rect)
            return level, doors, platforms, stairs
        elif floor_num == 5: 
            level = room1 
            for row_index, row in enumerate(room1): 
                for col_index, tile in enumerate(row): 
                    x = col_index * TILE_SIZE 
                    y = row_index * TILE_SIZE 
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE) 
                    match tile:
                        case "#": 
                            platforms.append(rect) 
                        case "L": 
                            doors.append(Door(rect, "any")) 
            return level, doors, platforms, stairs 
        else: 
            level = floors[floor_num] 
            door_keys.clear() 
            for row_index, row in enumerate(level): 
                for col_index, tile in enumerate(row): 
                    x = col_index * TILE_SIZE 
                    y = row_index * TILE_SIZE 
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE) 
                    match tile: 
                        case "#": 
                            platforms.append(rect) 
                        case "B": 
                            platforms.append(rect) 
                        case "S": 
                            stairs.append(rect) 
                        case "L": 
                            key_type = choice(available_keys) 
                            doors.append(Door(rect, key_type))
            floor_states[floor_num] = doors 
            return level, doors, platforms, stairs
    # --- Initialize first floor ---
    level, doors, platforms, stairs = setup_floor(current_floor)
    player1.x = 400
    player1.y = 500
    gravity = 2
    dx = 0
    jump_power = 15
    vel_y = 0
    on_ground = False
    health_font = pygame.font.Font(font_path, 20)
    font = pygame.font.Font(font_path, 24)
    font1 = pygame.font.Font(font_path, 60)
    message = ""
    duration = 600
    start_time = time()
    player1.health = 10
    bot = Player(2500, 600)  # start position for bot
    hide_knife_image_right = pygame.transform.rotate(hide_knife_image, -45)
    hide_knife_image_left = pygame.transform.rotate(hide_knife_image, 45)
    knife_swing_frames = 50
    swing_counter = 0
    swing_phase_delay = 25
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
    bot_move_direction = choice(["left", "right"])
    bot_speed = 0
    last_key_pressed = "right"
    has_attacked = False
    hide_played = False
    subtitle_start_time = time()
    subtitle_events = [
        (4, 3, ("Hide, hide, it's time to play", "숨어라, 숨어라, 놀 시간이야")),
        (7, 3, ("Don't let your hair give you away", "머리카락이 당신을 드러내지 않도록 하세요")),
        (10, 3, ("Hide, hide, it's time to play", "숨어라, 숨어라, 놀 시간이야")),
        (13, 3, ("Don't let your clothes give you away", "옷 때문에 자신을 드러내지 마세요")),
        (16, 3, ("Hide, hide, it's time to play", "숨어라, 숨어라, 놀 시간이야")),
        (19, 3, ("Don't let your toe give you away", "발가락이 당신을 드러내지 않도록 하세요")),
        (22, 3, ("Hide, hide, it's time to play", "숨어라, 숨어라, 놀 시간이야")),
        (25, 3, ("Don't let your hair give you away", "머리카락이 당신을 드러내지 않도록 하세요")),
        (28, 2, ("Hide, hide, it's time to play", "숨어라, 숨어라, 놀 시간이야")),
        (30, 3, ("Don't let your clothes give you away", "옷 때문에 자신을 드러내지 마세요")),
        (33, 3, ("Hide, hide, it's time to play", "숨어라, 숨어라, 놀 시간이야")),
        (36, 3, ("Don't let your toe give you away", "발가락이 당신을 드러내지 않도록 하세요")),
    ]
    font_korean = pygame.font.SysFont("malgungothic", 34)
    font_english = pygame.font.SysFont("Arial", 30)
    while True:
        clock.tick(60)
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
        if time() - start_time >= duration:
            match team:
                case "red":
                    player1.eliminated = True
                case "blue":
                    bot.eliminated = True
        if not hide_played:
            hide_theme_channel.play(hide_theme)
            hide_played = True
        time_left = duration - (time() - start_time)
        camera_x = player1.x - game_surface.get_width() // 2
        camera_y = player1.y - game_surface.get_height() // 2
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            last_key_pressed = "left"
            dx = -5
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            last_key_pressed = "right"
            dx = 5
        else:
            dx = 0
        bot_rect = pygame.Rect(bot.x, bot.y, 50, 100)
        player1_rect = pygame.Rect(player1.x, player1.y, 50, 100)
        player1.x += dx
        player1_rect.x = player1.x
        for platform in platforms:
            if player1_rect.colliderect(platform):
                if dx > 0:
                    player1_rect.right = platform.left
                elif dx < 0:
                    player1_rect.left = platform.right
                player1.x = player1_rect.x
        if on_ground and keys[pygame.K_SPACE]:
            vel_y = -jump_power
            on_ground = False
        elif not on_ground:
            vel_y += gravity
        player1.y += vel_y
        player1_rect.y = player1.y
        on_ground = False
        for platform in platforms:
            if player1_rect.colliderect(platform):
                if vel_y > 0:
                    player1_rect.bottom = platform.top
                    player1.y = player1_rect.y
                    vel_y = 0
                    on_ground = True
                # Hitting head
                elif vel_y < 0:
                    player1_rect.top = platform.bottom
                    player1.y = player1_rect.y
                    vel_y = 0
        for stair in stairs: 
            if player1_rect.colliderect(stair): 
                current_floor += 1 
                if current_floor > 3: 
                    current_floor = 1 
                level, doors, platforms, stairs = setup_floor(current_floor)
                player1.x = 400 
                player1.y = 500 
                bot.x = 2500
                bot.y = 600
                vel_y = 0 
                on_ground = False 
                player1_rect.x = player1.x 
                player1_rect.y = player1.y 
                break
        message = ""
        for door in doors:
            if player1_rect.colliderect(door.rect):
                if door.key_type == "any":
                    message = "Press E to Open (any key)"
                    if keys[pygame.K_e]:
                        if not pygame.mixer.Channel(0).get_busy():
                            unlock.play()
                        door.opened = True
                        level, doors, platforms, stairs = setup_floor(current_floor)
                        player1.x = 400
                        player1.y = 500
                        break
                elif door.opened:
                    message = "Press E to Open!"
                    if keys[pygame.K_e]:
                        if not pygame.mixer.Channel(0).get_busy():
                            unlock.play()
                        door.opened = True
                        level, doors, platforms, stairs = setup_floor(5)
                        player1.x = 100
                        player1.y = 100
                        break
                elif door.key_type in player_keys:
                    message = f"Press E to Open ({door.key_type} key)"
                    if keys[pygame.K_e]:
                        if not pygame.mixer.Channel(0).get_busy():
                            unlock.play()
                        door.opened = True
                        level, doors, platforms, stairs = setup_floor(5)
                        player1.x = 100
                        player1.y = 100
                        break
                else:
                    message = f"Door requires {door.key_type} key!"
        game_surface.blit(hide_background_image, (0, 0))
        for row_index, row in enumerate(level):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                match tile:
                    case "#":
                        pygame.draw.rect(game_surface, (87, 89, 86), pygame.Rect(x - camera_x, y - camera_y, TILE_SIZE, TILE_SIZE))
                    case "B":
                        pygame.draw.rect(game_surface, (0, 0, 255), pygame.Rect(x - camera_x, y - camera_y, TILE_SIZE, TILE_SIZE))
                    case "L":
                        game_surface.blit(door_image, (x - camera_x, y - camera_y))
                    case "S":
                        game_surface.blit(stairs_image, (x - camera_x, y - camera_y))
        if team == "red":
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
                        game_surface.blit(hide_knife_image, (player1.x + 50 - camera_x, player1.y - camera_y))
                    else:
                        game_surface.blit(hide_knife_image, (player1.x - 20 - camera_x, player1.y - camera_y))
                # Phase 1 → show tilted knife (attack frame)
                else:
                    if player1.knife_direction == "right":
                        knife_img = hide_knife_image_right
                        knife_offset = (player1.x + 40 - camera_x, player1.y - camera_y)
                    else:
                        knife_img = hide_knife_image_left
                        knife_offset = (player1.x - 65 - camera_x, player1.y - camera_y)
                    knife_rect = knife_img.get_rect(topleft=knife_offset)
                    game_surface.blit(knife_img, knife_offset)
                # Damage check only after swing_phase_delay
                if phase >= swing_phase_delay:
                    bot1_rect = pygame.Rect(bot.x - camera_x, bot.y - camera_y, 50, 100)
                    if knife_rect.colliderect(bot1_rect):
                        bot.health -= 1
                        if bot.health <= 0:
                            bot.eliminated = True
                swing_counter -= 1
            else:
                player1.knife_active = False
        if current_floor != 5:
            if not bot.eliminated and bot_team == "blue":
                bot_move_timer -= 1
                # Change direction every ~1 second
                if bot_move_timer <= 0:
                    bot_move_direction = choice(["left", "right"])
                    bot_move_timer = randint(20, 80)
                match bot_move_direction:
                    case "left":
                        bot_speed = -10
                    case  "right":
                        bot_speed = 10
                    case _:
                        bot_speed = 0
            elif not bot.eliminated and bot_team == "red":
                bot_move_timer -= 1
                bot_attack_timer -= 1
                # Change direction every ~1 second
                if bot_move_timer <= 0:
                    bot_move_direction = choice(["left", "right", "idle"])
                    bot_move_timer = randint(30, 60)
                # Move bot
                match bot_move_direction:
                    case "left":
                        bot_speed = -6
                        bot.knife_direction = "left"
                    case "right":
                        bot_speed = 6
                        bot.knife_direction = "right"
                    case _:
                        bot_speed = 0
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
                            game_surface.blit(hide_knife_image, (bot.x + 50 - camera_x, bot.y - camera_y))
                        else:
                            game_surface.blit(hide_knife_image, (bot.x - 20 - camera_x, bot.y - camera_y))
                    # Phase 1 → show tilted knife (attack frame)
                    else:
                        if bot.knife_direction == "right":
                            knife_img = hide_knife_image_right
                            knife_offset = (bot.x + 40 - camera_x, bot.y - camera_y)
                        else:
                            knife_img = hide_knife_image_left
                            knife_offset = (bot.x - 65 - camera_x, bot.y - camera_y)
                        knife_rect = knife_img.get_rect(topleft=knife_offset)
                        game_surface.blit(knife_img, knife_offset)
                        # Player hit detection
                        player_rect = pygame.Rect(player1.x - camera_x, player1.y - camera_y, 50, 100)
                        if knife_rect.colliderect(player_rect):
                            player1.health -= 1
                            if player1.health <= 0:
                                player1.eliminated = True
                    bot_swing_counter -= 1
                else:
                    bot.knife_active = False
        bot_rect = pygame.Rect(bot.x, bot.y, 50, 100)
        bot.x += bot_speed
        bot_rect.x = bot.x
        for platform in platforms:
            if bot_rect.colliderect(platform):
                if bot_speed > 0:
                    bot_rect.right = platform.left
                elif bot_speed < 0:
                    bot_rect.left = platform.right
                bot.x = bot_rect.x
        game_surface.blit(player_image, (player1.x - camera_x, player1.y - camera_y))
        match team:
            case "blue":
                game_surface.blit(blue_image, (player1.x - camera_x, player1.y + 37 - camera_y))
            case "red":
                game_surface.blit(red_image, (player1.x - camera_x, player1.y + 37 - camera_y))
        if freeplay == 0:
            game_surface.blit(o_patch_image, (player1.x - camera_x, player1.y - camera_y + 56))
        if not bot.eliminated:
            game_surface.blit(bot2_image, (bot.x - camera_x, bot.y - camera_y))
            match bot_team:
                case "red":
                    game_surface.blit(red_image, (bot.x - camera_x, bot.y + 37 - camera_y))
                case "blue":
                    game_surface.blit(blue_image, (bot.x - camera_x, bot.y + 37 - camera_y))
                    health_text = health_font.render(f"{int(bot.health)} HP", True, (255, 0, 0))
                    game_surface.blit(health_text, (bot.x - camera_x, bot.y - 20 - camera_y))
            if freeplay == 0:
                game_surface.blit(o_patch_image, (bot.x - camera_x, bot.y - camera_y + 56))
        if not has_attacked and team == "red":
            prompt_font = pygame.font.Font(font_path, 40)
            prompt_text = prompt_font.render("Press SPACE to Attack", True, (255, 255, 255))
            game_surface.blit(prompt_text, (game_surface.get_width() // 2 - prompt_text.get_width() // 2, 10))
        floor_text = font.render(f"Floor: {current_floor}", True, (255, 255, 255))
        if team == "blue":
            health_text = health_font.render(f"{int(player1.health)} HP", True, (255, 0, 0))
            game_surface.blit(health_text, (player1.x - camera_x, player1.y - 20 - camera_y))
            key_text = font.render(f"Key: {', '.join(player_keys)}", 1, (255, 255, 0))
            game_surface.blit(key_text, (10, 40))
            game_surface.blit(key_image, (key_text.get_width() + 10, 40))
        game_surface.blit(floor_text, (10, 10))
        if time_left <= 0:
            minut = 0
            sec = 0
        else:
            minut = time_left // 60
            sec = time_left % 60
        time_text = f"Time Left: {int(minut):02}:{int(sec):02}"
        match team:
            case "blue":
                game_surface.blit(font.render(time_text, 1, (255, 0, 0)), (10, 70))
                game_surface.blit(font.render(message, 1, (0, 255, 0)), (10, 100))
            case "red":
                game_surface.blit(font.render(message, 1, (0, 255, 0)), (10, 70))
                game_surface.blit(font.render(time_text, 1, (255, 0, 0)), (10, 40))
        elapsed = time() - subtitle_start_time
        current_english = ""
        current_korean = ""
        for start_t, duration1, (eng, kor) in subtitle_events:
            if start_t <= elapsed <= start_t + duration1:
                current_english = eng
                current_korean = kor
                break
        # Draw subtitle
        if current_english:
            eng_surface = font_english.render(current_english, True, (255, 0, 0))
            kor_surface = font_korean.render(current_korean, True, (255, 255, 255))
            game_surface.blit(kor_surface, (game_surface.get_width()//2 - kor_surface.get_width()//2, 600))
            game_surface.blit(eng_surface, (game_surface.get_width()//2 - eng_surface.get_width()//2, 640))
        if player1.eliminated:
            from menus import mainmenu
            hide_theme_channel.stop()
            lose_text = font1.render("You Lost...", True, (255, 0, 0))
            game_surface.blit(lose_text, (game_surface.get_width() // 2 - lose_text.get_width() // 2, 600))
            render_to_screen()
            sleep(3)
            player1.voted = False
            return mainmenu()
        elif bot.eliminated:
            hide_theme_channel.stop()
            win_text = font1.render("You WON!", True, (0, 255, 0))
            game_surface.blit(win_text, (game_surface.get_width() // 2 - win_text.get_width() // 2, 600))
            render_to_screen()
            sleep(3)
            match freeplay:
                case 1:
                    from menus import mainmenu
                    return mainmenu()
                case 0:
                    from lobby import lobby
                    lobby("Get Ready for Jump Rope!", 20, 0)
                    from jumprope import jumprope
                    return jumprope(0)
        render_to_screen()