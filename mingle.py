import pygame
from assets import background_mingle_image, background_mingle1_image, all_player_images, mingle_theme, mingle_welcomeback,  mingle_chaos
from player import player1, reset_player, sprite_id, player_image
from main import font_path
from sys import exit
from intro import play_intro_and_show_subtitles
from resize import is_fullscreen, toggle_fullscreen, handle_resize, render_to_screen, game_surface
from random import randint
from time import sleep, time
import player_selected
def mingle(freeplay=0):
    global sprite_id, player_image
    reset_player()
    if player_selected.selected_index is None:
        if freeplay == 1:
            sprite_id = randint(0, 22)
            player_image = all_player_images[sprite_id]
    else:
        player_image = all_player_images[player_selected.selected_index]
    play_intro_and_show_subtitles(13)
    player1.eliminated = False
    player1.in_door = False
    player1.mingle_win = False
    player1.in_door_id = None
    run = True
    clock = pygame.time.Clock()
    font = pygame.font.Font(font_path, 36)
    font1 = pygame.font.Font(font_path, 80)
    mingle_theme_played = False
    mingle_thanos_played = False
    mingle_chaos_played = False
    mingle_thanos_played = False
    current_round = 0
    door_positions = []
    mingle_start_time = time()
    MINGLE_DURATION = 470
    mingle_time_left = MINGLE_DURATION
    class Bot:
        def __init__(self, x, y, bot_id):
            self.x = x
            self.y = y
            self.bot_id = bot_id
            self.sprite_id = randint(0, 22)
            self.eliminated = False
            self.in_door = False
            self.in_door_id = None
            self.target_door = None
            self.move_timer = 0
            self.move_direction = [randint(-1, 1), randint(-1, 1)]
            self.door_check_timer = 0
            self.backup_doors = []
            self.door_commit_timer = 0
        def get_door_occupancy(self, door_positions, all_bots, player):
            """Count how many players/bots are in each door"""
            door_counts = {}
            for i, door_rect in enumerate(door_positions):
                count = 0
                if player.in_door_id == i and not player.eliminated:
                    count += 1
                for bot in all_bots:
                    if bot.in_door_id == i and not bot.eliminated and bot != self:
                        count += 1
                door_counts[i] = count
            return door_counts
        def update_movement(self, door_positions, current_round, all_bots, player, alive_count):
            is_door_phase = (
                (376 < mingle_time_left <= 406) or
                (282 < mingle_time_left <= 312) or
                (188 < mingle_time_left <= 218) or
                (94 < mingle_time_left <= 124) or
                (0 < mingle_time_left <= 30)
            )
            if is_door_phase and door_positions and not self.eliminated:
                players_needed = get_players_needed_per_door(current_round, alive_count)
                door_counts = self.get_door_occupancy(door_positions, all_bots, player)
                # Track how long this bot has been in same door
                if self.in_door and self.target_door == self.in_door_id:
                    self.door_commit_timer += 1
                else:
                    self.door_commit_timer = 0
                # If stuck in underfilled door > 4 seconds, abandon
                if (
                    self.in_door and
                    self.door_commit_timer > 240 and  # ~4 sec at 60fps
                    door_counts.get(self.in_door_id, 0) < players_needed
                ):
                    self.target_door = None
                    self.door_commit_timer = 0
                # Re-evaluate door choice occasionally or if no target
                self.door_check_timer += 1
                if self.target_door is None or self.door_check_timer > 5:
                    best_score = float("inf")
                    best_door = None
                    for i, rect in enumerate(door_positions):
                        count = door_counts[i]
                        if count >= players_needed:
                            continue  # skip full doors
                        dist = abs(self.x - rect.centerx) + abs(self.y - rect.centery)
                        score = dist
                        score += count * 50
                        match players_needed:
                            case 6:
                                match count: 
                                    case 2:
                                        score -= 1000
                                    case 3:
                                        score -= 1400
                                    case 4:
                                        score -= 1800
                            case 5:
                                match count: 
                                    case 2:
                                        score -= 1000
                                    case 3:
                                        score -= 1500
                            case 4:
                                if count == 2:
                                    score -= 1000
                        if count == players_needed - 1:
                            score -= 2000  # strong bonus → bots rush here
                        if count == 0:
                            score += 100
                        if score < best_score:
                            best_score = score
                            best_door = i
                    self.target_door = best_door
                    self.door_check_timer = 0
                # Move toward chosen door
                if self.target_door is not None:
                    rect = door_positions[self.target_door]
                    move_speed = 3
                    if mingle_time_left % 94 < 5:  # Panic if last 5s
                        move_speed = 5
                    if abs(self.x - rect.centerx) > 2:
                        self.x += move_speed if self.x < rect.centerx else -move_speed
                    if abs(self.y - rect.centery) > 2:
                        self.y += move_speed if self.y < rect.centery else -move_speed
            else:
                # Wander during music phase
                self.target_door = None
                self.door_check_timer = 0
                self.move_timer += 1
                if self.move_timer > randint(60, 180):  # change direction every 1–3 sec
                    self.move_direction = [randint(-2, 2), randint(-2, 2)]
                    self.move_timer = 0
                new_x = self.x + self.move_direction[0]
                new_y = self.y + self.move_direction[1]
                if 0 <= new_x <= game_surface.get_width() - 50:
                    self.x = new_x
                if 0 <= new_y <= game_surface.get_height() - 100:
                    self.y = new_y
            # Door collision check
            if door_positions and not self.eliminated:
                bot_rect = pygame.Rect(self.x, self.y, 50, 100)
                self.in_door = False
                self.in_door_id = None
                for i, door_rect in enumerate(door_positions):
                    if door_rect.colliderect(bot_rect):
                        self.in_door = True
                        self.in_door_id = i
                        break
            else:
                self.in_door = False
                self.in_door_id = None  
    bots = []
    for i in range(5):
        bot_x = randint(100, game_surface.get_width() - 150)
        bot_y = randint(200, game_surface.get_height() - 200)
        bot = Bot(bot_x, bot_y, i)
        bots.append(bot)
    DOOR_DATA = [
        {"x": 43, "y": 426, "width": 122, "height": 172},   # Door 1
        {"x": 253, "y": 414, "width": 103, "height": 202},  # Door 2
        {"x": 437, "y": 409, "width": 90, "height": 202},   # Door 3
        {"x": 603, "y": 407, "width": 91, "height": 202},   # Door 4
        {"x": 768, "y": 407, "width": 93, "height": 202},   # Door 5
        {"x": 938, "y": 409, "width": 101, "height": 202},  # Door 6
        {"x": 1123, "y": 414, "width": 116, "height": 202}  # Door 7
    ]
    def get_active_doors(num_doors_needed):
        """Get the specified number of doors from the available doors"""
        available_doors = DOOR_DATA[:min(num_doors_needed, len(DOOR_DATA))]
        return [pygame.Rect(door["x"], door["y"], door["width"], door["height"]) 
                for door in available_doors]
    players_needed_cache = {}
    def get_players_needed_per_door(round_num, alive_count):
        if round_num not in players_needed_cache:
            if round_num in (1, 2, 3, 4):
                players_needed_cache[round_num] = randint(1, alive_count)
            elif round_num == 5:
                players_needed_cache[round_num] = 1
        return players_needed_cache[round_num]
    def count_players_in_doors(entities, door_positions):
        counts = {i: 0 for i in range(len(door_positions))}
        for e in entities:
            if not e.eliminated and e.in_door_id is not None:
                counts[e.in_door_id] += 1
        return counts
    subtitle_start_time = time()
    subtitle_events = [
        (9, 2, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (11, 2, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (13, 5, ("Turning, Turning in a circle as we dance along", "돌고 돌며 춤을 추며")),
        (18, 2, ("Clapping our hands together", "우리 손을 함께 박수 치다")),
        (20, 3, ("Singing along as well", "노래도 따라 부르고")),
        (23, 4, ("La-la-la-la, let's dance happily together", "라라라라 함께 즐겁게 춤추자")),
        (27, 5, ("Ring-a Ring-a Riiiiiiing-a Ring-a Ring-a Ring", "링아 링아 리이이잉아 링아 링아 링")),
        (32, 4, ("Ring-a Ring-a Riiiiiiing-a Ring-a Ring-a Ring", "링아 링아 리이이잉아 링아 링아 링")),
        (36, 5, ("Hold your hands together, and all together", "손을 맞잡고, 모두 함께")),
        (41, 4, ("Let's run happily", "행복하게 달리자")),
        (45, 2, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (47, 3, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (50, 5, ("Turning, Turning in a circle as we dance along", "돌고 돌며 춤을 추며")),
        (55, 2, ("Clapping our hands together", "우리 손을 함께 박수 치다")),
        (57, 2, ("Singing along as well", "노래도 따라 부르고")),
        (59, 5, ("La-la-la-la, let's dance happily together", "라라라라 함께 즐겁게 춤추자")),
        (103, 2, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (105, 2, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (107, 5, ("Turning, Turning in a circle as we dance along", "돌고 돌며 춤을 추며")),
        (112, 2, ("Clapping our hands together", "우리 손을 함께 박수 치다")),
        (114, 3, ("Singing along as well", "노래도 따라 부르고")),
        (117, 4, ("La-la-la-la, let's dance happily together", "라라라라 함께 즐겁게 춤추자")),
        (121, 5, ("Ring-a Ring-a Riiiiiiing-a Ring-a Ring-a Ring", "링아 링아 리이이잉아 링아 링아 링")),
        (126, 4, ("Ring-a Ring-a Riiiiiiing-a Ring-a Ring-a Ring", "링아 링아 리이이잉아 링아 링아 링")),
        (130, 5, ("Hold your hands together, and all together", "손을 맞잡고, 모두 함께")),
        (135, 4, ("Let's run happily", "행복하게 달리자")),
        (139, 2, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (141, 3, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (144, 5, ("Turning, Turning in a circle as we dance along", "돌고 돌며 춤을 추며")),
        (149, 2, ("Clapping our hands together", "우리 손을 함께 박수 치다")),
        (151, 2, ("Singing along as well", "노래도 따라 부르고")),
        (153, 5, ("La-la-la-la, let's dance happily together", "라라라라 함께 즐겁게 춤추자")),
        (197, 2, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (199, 2, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (201, 5, ("Turning, Turning in a circle as we dance along", "돌고 돌며 춤을 추며")),
        (206, 2, ("Clapping our hands together", "우리 손을 함께 박수 치다")),
        (208, 3, ("Singing along as well", "노래도 따라 부르고")),
        (211, 4, ("La-la-la-la, let's dance happily together", "라라라라 함께 즐겁게 춤추자")),
        (215, 5, ("Ring-a Ring-a Riiiiiiing-a Ring-a Ring-a Ring", "링아 링아 리이이잉아 링아 링아 링")),
        (220, 4, ("Ring-a Ring-a Riiiiiiing-a Ring-a Ring-a Ring", "링아 링아 리이이잉아 링아 링아 링")),
        (224, 5, ("Hold your hands together, and all together", "손을 맞잡고, 모두 함께")),
        (229, 4, ("Let's run happily", "행복하게 달리자")),
        (233, 2, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (235, 3, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (238, 5, ("Turning, Turning in a circle as we dance along", "돌고 돌며 춤을 추며")),
        (243, 2, ("Clapping our hands together", "우리 손을 함께 박수 치다")),
        (245, 2, ("Singing along as well", "노래도 따라 부르고")),
        (247, 5, ("La-la-la-la, let's dance happily together", "라라라라 함께 즐겁게 춤추자")),
        (291, 2, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (293, 2, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (295, 5, ("Turning, Turning in a circle as we dance along", "돌고 돌며 춤을 추며")),
        (300, 2, ("Clapping our hands together", "우리 손을 함께 박수 치다")),
        (302, 3, ("Singing along as well", "노래도 따라 부르고")),
        (305, 4, ("La-la-la-la, let's dance happily together", "라라라라 함께 즐겁게 춤추자")),
        (309, 5, ("Ring-a Ring-a Riiiiiiing-a Ring-a Ring-a Ring", "링아 링아 리이이잉아 링아 링아 링")),
        (314, 4, ("Ring-a Ring-a Riiiiiiing-a Ring-a Ring-a Ring", "링아 링아 리이이잉아 링아 링아 링")),
        (318, 5, ("Hold your hands together, and all together", "손을 맞잡고, 모두 함께")),
        (323, 4, ("Let's run happily", "행복하게 달리자")),
        (327, 2, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (329, 3, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (332, 5, ("Turning, Turning in a circle as we dance along", "돌고 돌며 춤을 추며")),
        (337, 2, ("Clapping our hands together", "우리 손을 함께 박수 치다")),
        (339, 2, ("Singing along as well", "노래도 따라 부르고")),
        (341, 5, ("La-la-la-la, let's dance happily together", "라라라라 함께 즐겁게 춤추자")),
        (385, 2, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (387, 2, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (389, 5, ("Turning, Turning in a circle as we dance along", "돌고 돌며 춤을 추며")),
        (394, 2, ("Clapping our hands together", "우리 손을 함께 박수 치다")),
        (396, 3, ("Singing along as well", "노래도 따라 부르고")),
        (399, 4, ("La-la-la-la, let's dance happily together", "라라라라 함께 즐겁게 춤추자")),
        (403, 5, ("Ring-a Ring-a Riiiiiiing-a Ring-a Ring-a Ring", "링아 링아 리이이잉아 링아 링아 링")),
        (408, 4, ("Ring-a Ring-a Riiiiiiing-a Ring-a Ring-a Ring", "링아 링아 리이이잉아 링아 링아 링")),
        (412, 5, ("Hold your hands together, and all together", "손을 맞잡고, 모두 함께")),
        (417, 4, ("Let's run happily", "행복하게 달리자")),
        (421, 2, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (423, 3, ("Round and round we go", "우리는 빙빙 돌아간다")),
        (426, 5, ("Turning, Turning in a circle as we dance along", "돌고 돌며 춤을 추며")),
        (431, 2, ("Clapping our hands together", "우리 손을 함께 박수 치다")),
        (433, 2, ("Singing along as well", "노래도 따라 부르고")),
        (435, 5, ("La-la-la-la, let's dance happily together", "라라라라 함께 즐겁게 춤추자")),
    ]
    font_korean = pygame.font.SysFont("malgungothic", 34)
    font_english = pygame.font.SysFont("Arial", 30)
    while run:
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
        alive_count = 1 if not player1.eliminated else 0
        alive_count += sum(1 for bot in bots if not bot.eliminated)
        mingle_elapsed = time() - mingle_start_time
        mingle_time_left = max(0, MINGLE_DURATION - int(mingle_elapsed))
        for bot in bots:
            if not bot.eliminated:
                bot.update_movement(door_positions, current_round, bots, player1, alive_count)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            player1.x += 5
            if player1.x > game_surface.get_width() - 50:
                player1.x -= 5
        elif keys[pygame.K_LEFT]:
            player1.x -= 5
            if player1.x < 0:
                player1.x += 5
        if keys[pygame.K_UP]:
            player1.y -= 5
            if player1.y < 0:
                player1.y += 5
        elif keys[pygame.K_DOWN]:
            player1.y += 5
            if player1.y > game_surface.get_height() - 100:
                player1.y -= 5
        elapsed = time() - subtitle_start_time
        if mingle_time_left > 406:
            game_surface.blit(background_mingle_image, (0, 0))
            if not mingle_theme_played:
                mingle_theme.play()
                mingle_theme_played = True
        elif mingle_time_left > 376:
            game_surface.blit(background_mingle1_image, (0, 0))
            mingle_theme_played = False
            if not mingle_chaos_played:
                mingle_chaos.play()
                mingle_chaos_played = True
            if current_round != 1:
                current_round = 1
                door_positions = get_active_doors(7)
            countdown = mingle_time_left - 376
            text_surface = font1.render(str(countdown), True, (255, 255, 255))
            game_surface.blit(text_surface, (game_surface.get_width() // 2 - text_surface.get_width() // 2, 200))
        elif mingle_time_left > 312:
            game_surface.blit(background_mingle_image, (0, 0))
            mingle_chaos_played = False
            if not mingle_thanos_played and sprite_id == 18:
                mingle_welcomeback.play()
                mingle_thanos_played = True
            if not mingle_theme_played:
                mingle_theme.play()
                mingle_theme_played = True
        elif mingle_time_left > 282:
            game_surface.blit(background_mingle1_image, (0, 0))
            mingle_theme_played = False
            mingle_thanos_played = False
            if not mingle_chaos_played:
                mingle_chaos.play()
                mingle_chaos_played = True
            if current_round != 2:
                current_round = 2
                door_positions = get_active_doors(7)
            countdown = mingle_time_left - 282
            text_surface = font1.render(str(countdown), True, (255, 255, 255))
            game_surface.blit(text_surface, (game_surface.get_width() // 2 - text_surface.get_width() // 2, 200))
        elif mingle_time_left > 218:
            game_surface.blit(background_mingle_image, (0, 0))
            mingle_chaos_played = False
            if not mingle_thanos_played and sprite_id == 18:
                mingle_welcomeback.play()
                mingle_thanos_played = True
            if not mingle_theme_played:
                mingle_theme.play()
                mingle_theme_played = True
        elif mingle_time_left > 188:
            game_surface.blit(background_mingle1_image, (0, 0))
            mingle_theme_played = False
            mingle_thanos_played = False
            if not mingle_chaos_played:
                mingle_chaos.play()
                mingle_chaos_played = True
            if current_round != 3:
                current_round = 3
                door_positions = get_active_doors(7)
            countdown = mingle_time_left - 188
            text_surface = font1.render(str(countdown), True, (255, 255, 255))
            game_surface.blit(text_surface, (game_surface.get_width() // 2 - text_surface.get_width() // 2, 200))
        elif mingle_time_left > 124:
            game_surface.blit(background_mingle_image, (0, 0))
            mingle_chaos_played = False
            if not mingle_thanos_played and sprite_id == 18:
                mingle_welcomeback.play()
                mingle_thanos_played = True
            if not mingle_theme_played:
                mingle_theme.play()
                mingle_theme_played = True
        elif mingle_time_left > 94:
            game_surface.blit(background_mingle1_image, (0, 0))
            mingle_theme_played = False
            mingle_thanos_played = False
            if not mingle_chaos_played:
                mingle_chaos.play()
                mingle_chaos_played = True
            if current_round != 4:
                current_round = 4
                door_positions = get_active_doors(7)
            countdown = mingle_time_left - 94
            text_surface = font1.render(str(countdown), True, (255, 255, 255))
            game_surface.blit(text_surface, (game_surface.get_width() // 2 - text_surface.get_width() // 2, 200))
        elif mingle_time_left > 30:
            game_surface.blit(background_mingle_image, (0, 0))
            mingle_chaos_played = False
            if not mingle_thanos_played and sprite_id == 18:
                mingle_welcomeback.play()
                mingle_thanos_played = True
            if not mingle_theme_played:
                mingle_theme.play()
                mingle_theme_played = True
        elif mingle_time_left > 0:
            game_surface.blit(background_mingle1_image, (0, 0))
            if not mingle_chaos_played:
                mingle_chaos.play()
                mingle_chaos_played = True
            if current_round != 5:
                current_round = 5
                door_positions = get_active_doors(7)
            countdown = mingle_time_left
            text_surface = font1.render(str(countdown), True, (255, 255, 255))
            game_surface.blit(text_surface, (game_surface.get_width() // 2 - text_surface.get_width() // 2, 200))
        # Draw door overlays and player counts when doors are active (whenever background_mingle1_image is shown)
        if mingle_time_left <= 406 and mingle_time_left > 0 and current_round > 0:
            # Skip the preparation phases
            if not (312 < mingle_time_left <= 376 or 218 < mingle_time_left <= 282 or 
                   124 < mingle_time_left <= 188 or 30 < mingle_time_left <= 94):
                # Check if player is near a door
                if door_positions and not player1.eliminated:
                    player_rect = pygame.Rect(player1.x, player1.y, 50, 100)
                    player1.in_door = False
                    player1.in_door_id = None
                    for i, door_rect in enumerate(door_positions):
                        if door_rect.colliderect(player_rect):
                            player1.in_door = True
                            player1.in_door_id = i
                            break
                # Draw round display and door overlays
                if door_positions:
                    round_text = font.render(f"Round {current_round}/5", True, (255, 255, 255))
                    game_surface.blit(round_text, (10, 50))
                    players_needed = get_players_needed_per_door(current_round, alive_count)
                    door_counts = count_players_in_doors([player1] + bots, door_positions)
                    for i, door_rect in enumerate(door_positions):
                        # Draw door overlay
                        overlay = pygame.Surface((door_rect.width, door_rect.height))
                        overlay.set_alpha(30)
                        if player1.in_door_id == i:
                            overlay.fill((0, 255, 0))  # Green if player is in this door
                        else:
                            overlay.fill((100, 100, 100))  # Gray otherwise
                        game_surface.blit(overlay, (door_rect.x, door_rect.y))
                        # Draw player count (in single player, show 1 if player is in door, 0 if not)
                        players_inside = door_counts.get(i, 0)
                        count_text = f"{players_inside}/{players_needed}"
                        # Color code the text
                        if players_inside == players_needed:
                            count_color = (0, 255, 0)  # Green if correct
                        elif players_inside > players_needed:
                            count_color = (255, 0, 0)
                        elif players_inside < players_needed:
                            count_color = (255, 255, 255)  # White if not correct
                        count_surface = font.render(count_text, True, count_color)
                        count_rect = count_surface.get_rect(center=(door_rect.centerx, door_rect.y - 15))
                        game_surface.blit(count_surface, count_rect)
                if countdown == 1:
                    players_needed = get_players_needed_per_door(current_round, alive_count)
                    safe_doors = set()
                    for i, door_rect in enumerate(door_positions):
                        door_player_count = door_counts.get(i, 0)
                        if door_player_count == players_needed:
                            safe_doors.add(i)
                    if player1.in_door_id is None or player1.in_door_id not in safe_doors:
                        player1.eliminated = True
                    elif current_round == 5 and player1.in_door_id in safe_doors:
                        player1.mingle_win = True
                    for bot in bots:
                        if not bot.eliminated:
                            if bot.in_door_id is None or bot.in_door_id not in safe_doors:
                                bot.eliminated = True
        for bot in bots:
            if not bot.eliminated:
                bot_image = all_player_images[bot.sprite_id]
                game_surface.blit(bot_image, (bot.x, bot.y))  # Offset to center
        game_surface.blit(player_image, (player1.x, player1.y))
        current_english = ""
        current_korean = ""
        for start_t, duration, (eng, kor) in subtitle_events:
            if start_t <= elapsed <= start_t + duration:
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
            lose_text = font.render("You Lost...", True, (255, 0, 0))
            game_surface.blit(lose_text, (game_surface.get_width() // 2 - lose_text.get_width() // 2, 600))
            pygame.display.flip()
            sleep(3)
            return mainmenu()
        elif player1.mingle_win:
            win_text = font.render("You Won Mingle!", True, (0, 255, 0))
            game_surface.blit(win_text, (game_surface.get_width() // 2 - win_text.get_width() // 2, 600))
            pygame.display.flip()
            sleep(3)
            match freeplay:
                case 0:
                    from lobby import lobby
                    lobby("Get Ready for Hide-n-Seek!", 40, 1)
                    from hide import hide
                    return hide()
                case 1:
                    from menus import mainmenu
                    return mainmenu()
        render_to_screen()