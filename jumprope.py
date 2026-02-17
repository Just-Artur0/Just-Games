import pygame
from math import pi, sin, radians
from time import time, sleep
from main import font_path
from sys import exit
from random import randint
from resize import game_surface, render_to_screen, is_fullscreen, toggle_fullscreen, handle_resize
from assets import jump_background_image, doll1_image, doll2_image, doll1house_image, doll2house_image, jump_theme, tugofwar_theme, o_patch_image, baby_image
from player import player1, reset_player, player_image, all_player_images
from intro import play_intro_and_show_subtitles
import player_selected
def jumprope(freeplay=0):
    global player_image
    if player_selected.selected_index is None:
        if freeplay == 1:
            sprite_id = randint(0, 22)
            player_image = all_player_images[sprite_id]
    else:
        player_image = all_player_images[player_selected.selected_index]
    reset_player()
    play_intro_and_show_subtitles(15)
    jump_theme.play()
    font = pygame.font.Font(font_path, 36)
    rope_angle = 0
    rope_speed = 4
    duration = 300
    start_time = time()
    subtitle_start_time = time()
    time_left = 0
    left_doll_x = 700
    right_doll_x = 2500
    doll_y = 450
    gravity = 1
    vel_y = 0
    jump_power = 12
    on_ground = False
    fall = False
    player1.x = 100
    player1.y = 300
    clock = pygame.time.Clock()
    TILE_SIZE = 50
    level = ["#                                                           #",
             "#                                                           #",
             "#                                                           #",
             "#                                                           #",
             "#                                                           #",
             "#             S                                 S           #",
             "#                                                           #",
             "#                                                           #",
             "##############################   ############################"]
    subtitle_events = [
        (3, 2, ("Knock, knock", "똑, 똑")),
        (5, 3, ("Who is there?", "거기 누가 있나요?")),
        (8, 2, ("Your little friend", "당신의 작은 친구")),
        (10, 3, ("Come on in", "들어오세요")),
        (13, 2, ("Little friend, little friend", "작은 친구, 작은 친구")),
        (15, 3, ("Turn around", "돌아서다")),
        (18, 2, ("Little friend, little friend", "작은 친구, 작은 친구")),
        (20, 3, ("Touch the ground", "땅을 만지다")),
        (23, 2, ("Little friend, little friend", "작은 친구, 작은 친구")),
        (25, 3, ("Touch your toe", "발가락을 만지다")),
        (28, 2, ("Little friend, little friend", "작은 친구, 작은 친구")),
        (30, 3, ("Now away you go", "이제 가세요")),
        (33, 2, ("Little friend, little friend", "작은 친구, 작은 친구")),
        (35, 3, ("Turn around", "돌아서다")),
        (38, 2, ("Little friend, little friend", "작은 친구, 작은 친구")),
        (40, 3, ("Touch the ground", "땅을 만지다")),
        (43, 2, ("Little friend, little friend", "작은 친구, 작은 친구")),
    ]
    font_korean = pygame.font.SysFont("malgungothic", 34)
    font_english = pygame.font.SysFont("Arial", 30)
    tug_played = False
    elapsed = 0
    baby_rect = pygame.Rect(120, 360, 50, 39)
    baby_pickable = False
    baby_picked = False
    baby_text = font.render("Press E to Pick Up Baby", True, (255, 255, 0))
    scaled_baby = pygame.transform.scale(baby_image, (125, 120))
    platforms = []
    for row_i, row in enumerate(level):
            for col_i, tile in enumerate(row):
                x = col_i * TILE_SIZE
                y = row_i * TILE_SIZE
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                if tile == "#":
                    platforms.append(rect)
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
        if time() - start_time >= 45 and not tug_played:
            tugofwar_theme.play(-1)
            tug_played = True
        time_left = duration - (time() - start_time)
        camera_x = player1.x - game_surface.get_width() // 2
        camera_y = player1.y - game_surface.get_height() // 2
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -5
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 5
        else:
            dx = 0
        if baby_pickable and keys[pygame.K_e]:
            baby_picked = True
        player1.x += dx
        player1_rect = pygame.Rect(player1.x, player1.y, 50, 100)
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
                if fall:
                    break
                if vel_y > 0:
                    player1_rect.bottom = platform.top
                    player1.y = player1_rect.y
                    vel_y = 0
                    on_ground = True
                elif vel_y < 0:
                    player1_rect.top = platform.bottom
                    player1.y = player1_rect.y
                    vel_y = 0
        if player1_rect.colliderect(baby_rect):
            baby_pickable = True
        else:
            baby_pickable = False
        game_surface.fill((25, 1, 167))
        game_surface.blit(jump_background_image, (-10 - camera_x, -300 - camera_y))
        rope_angle += rope_speed
        if rope_angle >= 360:
            rope_angle -= 360
        # Rope endpoints
        p1 = (left_doll_x, doll_y)
        p2 = (right_doll_x, doll_y)
        # Number of segments used to draw curved rope
        segments = 40
        # Height of the rope arc (changes while spinning)
        wave_height = sin(radians(rope_angle)) * 220  # how high rope goes
        # Draw rope as connected points
        points = []
        for i in range(segments + 1):
            t = i / segments
            # Linear interpolation between endpoints
            x = p1[0] * (1 - t) + p2[0] * t
            y = p1[1] * (1 - t) + p2[1] * t
            # Add curvature using sine wave
            curve = sin(t * pi) * wave_height
            y += curve
            points.append((x - camera_x, y - camera_y - 200))
        # ---- COLLISION WITH PLAYER ----
        player_rect = pygame.Rect(player1.x, player1.y, 50, 100)
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i+1]
            # Build a tiny rect around each rope segment
            seg_rect = pygame.Rect(
                min(x1, x2),
                min(y1, y2),
                abs(x2 - x1) + 8,   # thickness
                abs(y2 - y1) + 8
            )
            if seg_rect.colliderect(player_rect.move(-camera_x, -camera_y)):
                if on_ground and wave_height > 145:
                    fall = True
        game_surface.blit(doll1house_image, (-200 - camera_x, 0 - camera_y))
        game_surface.blit(doll2house_image, (2800 - camera_x, 0 - camera_y))
        if wave_height > 135:
            game_surface.blit(player_image, (player1.x - camera_x, player1.y - camera_y))
            if freeplay == 0:
                game_surface.blit(o_patch_image, (player1.x - camera_x, player1.y - camera_y + 56))
            if not baby_picked:
                game_surface.blit(scaled_baby, (120 - camera_x, 360 - camera_y))
            elif baby_picked:
                game_surface.blit(baby_image, (player1.x - camera_x, player1.y - camera_y + 61))
            pygame.draw.lines(game_surface, (150, 75, 0), False, points, 8)
        else:
            pygame.draw.lines(game_surface, (150, 75, 0), False, points, 8)
            game_surface.blit(player_image, (player1.x - camera_x, player1.y - camera_y))
            if freeplay == 0:
                game_surface.blit(o_patch_image, (player1.x - camera_x, player1.y - camera_y + 56))
            if not baby_picked:
                game_surface.blit(scaled_baby, (120 - camera_x, 360 - camera_y))
            elif baby_picked:
                game_surface.blit(baby_image, (player1.x - camera_x, player1.y - camera_y + 61))
        if player1.y > 1060:
            fall = False
            player1.x = 100
            player1.y = 300
        game_surface.blit(doll1_image, (550 - camera_x, 0 - camera_y))
        game_surface.blit(doll2_image, (2450 - camera_x, -20 - camera_y))
        if time() - start_time >= duration:
            if player1.x >= 2400:
                win_text = font.render("You WON!", True, (0, 255, 0))
                game_surface.blit(win_text, (game_surface.get_width() // 2 - win_text.get_width() // 2, 600))
                render_to_screen()
                sleep(3)
                tugofwar_theme.stop()
                if freeplay == 0:
                    player1.baby_picked = True
                    from lobby import lobby
                    lobby("Get Ready for Sky Squid Game!", 20, 0)
                    from sky import sky
                    return sky(0)
                elif freeplay == 1:
                    from menus import mainmenu
                    return mainmenu()
            elif player1.x < 2500:
                player1.eliminated = True
        if player1.eliminated:
            from menus import mainmenu
            lose_text = font.render("You Lost...", True, (255, 0, 0))
            game_surface.blit(lose_text, (game_surface.get_width() // 2 - lose_text.get_width() // 2, 600))
            render_to_screen()
            sleep(3)
            player1.voted = False
            tugofwar_theme.stop()
            return mainmenu()
        if baby_pickable and not baby_picked:
            game_surface.blit(baby_text, (game_surface.get_width() // 2 - baby_text.get_width() // 2, 550))
        minut = time_left // 60
        sec = time_left % 60
        time_text = f"{int(minut):02}:{int(sec):02}"
        game_surface.blit(font.render(time_text, 1, (255, 45, 8)), (600, 0))
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
        render_to_screen()