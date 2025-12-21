import pygame
from sys import exit
from time import sleep, time
from player import player1, reset_player, sprite_id, player_image
from assets import square_image, circle_image, triangle_image, all_player_images, finalist_suit_image, pole_image, baby_image, o_patch_image, drop_baby_image, sacrifice_image
from assets import sky_voiceline1, sky_voiceline2, sky_voiceline3, sky_voiceline4, sky_voiceline5, sky_background1_image, sky_background2_image, sky_background3_image, sky_background4_image
from assets import sky_background5_image, sky_end
from resize import game_surface, render_to_screen, handle_resize, is_fullscreen, toggle_fullscreen, scale_mouse_pos
from random import randint
from main import font_path
from intro import play_intro_and_show_subtitles
import player_selected
def play_end():
    global sprite_id, player_image
    if player_selected.selected_index is not None:
        player_image = all_player_images[player_selected.selected_index]
    player_scaled = pygame.transform.scale(player_image, (978, 1400)).convert_alpha()
    subtitles = [
        ("우리는 말이 아닙니다.", 
        "We are not horses.", 
        6000, sky_background1_image),
        ("우리는 인간입니다.", 
        "We are humans.", 
        11000, sky_background1_image),
        ("인간은...", 
        "Humans are...", 
        8000, sky_background1_image),
        ("", 
        "", 
        27000, sky_background2_image),
        ("", 
        "", 
        10000, sky_background3_image),
        ("", 
        "", 
        33000, sky_background4_image),
        ("", 
        "", 
        4500, sky_background5_image),
        ("게임이 끝났습니다.", 
        "The game is over.", 
        2500, sky_background5_image),
    ]
    intro_voice_channel = pygame.mixer.Channel(7)
    intro_voice_channel.play(sky_end)
    font_korean = pygame.font.SysFont("malgungothic", 34)
    font_english = pygame.font.SysFont("Arial", 30)
    player_c = 0
    player_cs = False
    clock = pygame.time.Clock()
    for kr, en, duration, intro_background_image in subtitles:
        start_time = pygame.time.get_ticks()
        running = True
        while running:
            clock.tick(5)
            now = pygame.time.get_ticks()
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
            if not player_cs:
                player_c += 1
                player_cs = True
            game_surface.blit(intro_background_image, (0, 0))
            if player_c <= 3:
                game_surface.blit(player_scaled, (206, 0))
            kr_text = font_korean.render(kr, True, (255, 255, 255))
            en_text = font_english.render(en, True, (255, 0, 0))
            game_surface.blit(kr_text, (game_surface.get_width()//2 - kr_text.get_width()//2, 560))
            game_surface.blit(en_text, (game_surface.get_width()//2 - en_text.get_width()//2, 600))
            render_to_screen()
            if now - start_time >= duration:
                running = False
                player_cs = False
def sky(freeplay=0):
    global sprite_id, player_image
    reset_player()
    play_intro_and_show_subtitles(16)
    if player_selected.selected_index is None:
        if freeplay == 1:
            sprite_id = randint(0, 22)
            player_image = all_player_images[sprite_id]
    else:
        player_image = all_player_images[player_selected.selected_index]
    bridge1_done = False
    bridge2_done = False
    class Bot:
        def __init__(self, x, y, image, target="square"):
            self.x = x
            self.y = y
            self.image = image
            self.target = target
            self.vx = randint(-2, 2) or 1
            self.vy = randint(-2, 2) or 1
            self.speed = 2
            self.state = "roam"
            self.state_timer = time()
            self.attack_target = None
            self.eliminated = False
            self.push_velocity = [0, 0]
            self.last_push_time = 0
            self.push_cooldown = 3.0  # Longer cooldown for bots
            self.has_elimination_in_zone = False  # Track if someone was eliminated in this zone
            self.moving_to_next_zone = False  # Track if bot is moving to next platform
            self.next_zone_target = None  # Target for next zone
        def get_zone(self):
            if self.target == "square":
                return square_rect
            elif self.target == "triangle":
                return triangle_rect
            return circle_rect
        def pick_random_direction(self):
            self.vx = randint(-self.speed, self.speed) or 1
            self.vy = randint(-self.speed, self.speed) or 1
        def apply_push(self, force_x, force_y):
            self.push_velocity[0] += force_x
            self.push_velocity[1] += force_y
        def try_push(self, target, push_force=80):
            """Attempt to push a target player/bot"""
            current_time = time()
            if current_time - self.last_push_time < self.push_cooldown:
                return False
            # Calculate direction to target
            dx = target.x - self.x
            dy = target.y - self.y
            dist = abs(dx) + abs(dy)
            # Only push if close enough (within 60 pixels)
            if dist < 60 and dist > 0:
                # Normalize direction and apply push
                length = max(1, abs(dx) + abs(dy))
                push_x = int(dx / length * push_force)
                push_y = int(dy / length * push_force)
                target.apply_push(push_x, push_y)
                self.last_push_time = current_time
                return True
            return False
        def update(self, players, elimination_happened_in_zone=False, task_completed=False, button_pressed=False):
            zone = self.get_zone()
            bot_rect = pygame.Rect(self.x, self.y, 50, 100)
            # -------- ZONE TRANSITION LOGIC --------
            if task_completed and not self.moving_to_next_zone:
                self.moving_to_next_zone = True
                self.state = "transition"
            if self.moving_to_next_zone:
                # First, move to y = 300
                if abs(self.y - 300) > 5:
                    if self.y < 300:
                        self.y += 3
                    else:
                        self.y -= 3
                    self.vy = 0
                    self.vx = 0
                else:
                    # Once at y = 300, move right towards next zone
                    self.y = 300
                    if self.target == "square" and bridge1_done:
                        # Move to triangle
                        if self.x < 1460:  # Center of triangle
                            self.x += 4
                            self.vx = 0
                            self.vy = 0
                        else:
                            # Reached triangle
                            self.moving_to_next_zone = False
                            self.target = "triangle"
                            self.state = "roam"
                            self.state_timer = time()
                    elif self.target == "triangle" and bridge2_done:
                        # Move to circle
                        if self.x < 2280:  # Center of circle
                            self.x += 4
                            self.vx = 0
                            self.vy = 0
                        else:
                            # Reached circle
                            self.moving_to_next_zone = False
                            self.target = "circle"
                            self.state = "roam"
                            self.state_timer = time()
                return  # Skip normal behavior during transition
            # -------- ATTACK LOGIC --------
            nearest = None
            nearest_dist = 9999
            for p in players:
                if p == self or p.eliminated:
                    continue
                dx = p.x - self.x
                dy = p.y - self.y
                dist = abs(dx) + abs(dy)
                if dist < nearest_dist:
                    nearest = p
                    nearest_dist = dist
            # Only attack/push if button is pressed, no elimination has happened, and button was pressed
            if button_pressed and not elimination_happened_in_zone:
                if nearest and nearest_dist < 120:
                    self.state = "attack"
                    self.attack_target = nearest
                    # Try to push when close enough
                    self.try_push(nearest, push_force=120)
                else:
                    self.state = "roam"
                    self.attack_target = None
            else:
                self.state = "roam"
                self.attack_target = None
            # -------- STATE BEHAVIOR --------
            if self.state == "attack" and self.attack_target:
                dx = self.attack_target.x - self.x
                dy = self.attack_target.y - self.y
                length = max(1, abs(dx) + abs(dy))
                self.vx = int(dx / length * self.speed)
                self.vy = int(dy / length * self.speed)
            elif self.state == "roam":
                # Pick a new random direction every 1–2 seconds
                if time() - self.state_timer > 1.5:
                    self.pick_random_direction()
                    self.state_timer = time()
            # -------- APPLY MOVEMENT + PUSH --------
            self.x += self.vx + self.push_velocity[0]
            self.y += self.vy + self.push_velocity[1]
            # Decay push velocity (higher value = more slide/momentum)
            self.push_velocity[0] *= 0.02
            self.push_velocity[1] *= 0.02
            # -------- ZONE BOUNDS (with pixel-perfect checking) --------
            # Check edge detection for both roaming and when push is low
            if abs(self.push_velocity[0]) < 5 and abs(self.push_velocity[1]) < 5:
                # Check current position first
                if not check_on_platform(self.x, self.y, width=50, height=100):
                    # Currently off platform! Emergency correction
                    self.x -= self.vx * 8
                    self.y -= self.vy * 8
                    self.vx = -self.vx
                    self.vy = -self.vy
                    self.pick_random_direction()
                else:
                    # Check if bot would be on solid ground if it continues moving
                    check_distance = 25  # Look even further ahead
                    future_x = self.x + (self.vx * check_distance)
                    future_y = self.y + (self.vy * check_distance)
                    # Use the proper width/height check
                    if not check_on_platform(future_x, future_y, width=50, height=100):
                        # Would fall off, so reverse direction
                        self.vx = -self.vx
                        self.vy = -self.vy
                        self.pick_random_direction()
                        # Move back to safety
                        self.x -= self.vx * 8
                        self.y -= self.vy * 8
    bots = [
        Bot(600, 300, all_player_images[randint(0, 22)]),
        Bot(700, 350, all_player_images[randint(0, 22)]),
        Bot(800, 300, all_player_images[randint(0, 22)])
    ]
    player1.x = 500
    player1.y = 300
    player1.push_velocity = [0, 0]  # Add push velocity to player
    def apply_push_to_player(force_x, force_y):
        """Apply push force to player"""
        if not hasattr(player1, 'push_velocity'):
            player1.push_velocity = [0, 0]
        player1.push_velocity[0] += force_x
        player1.push_velocity[1] += force_y
    player1.apply_push = apply_push_to_player
    square_rect = pygame.Rect(330, 50, 620, 620)
    triangle_rect = pygame.Rect(1150, 50, 620, 620)
    circle_rect = pygame.Rect(1970, 50, 620, 620)
    square_mask = pygame.mask.from_surface(square_image)
    triangle_mask = pygame.mask.from_surface(triangle_image)
    circle_mask = pygame.mask.from_surface(circle_image)
    def check_on_platform(x, y, width=50, height=100):
        """Check if position (x, y) with given width/height is on any non-transparent pixel of platforms"""
        # Check multiple points across the entity's entire body
        points_to_check = [
            # Bottom row (feet) - MOST IMPORTANT
            (x + 5, y + height - 5),               # Bottom far left
            (x + width // 4, y + height - 5),      # Bottom left
            (x + width // 2, y + height - 5),      # Bottom center
            (x + 3 * width // 4, y + height - 5),  # Bottom right
            (x + width - 5, y + height - 5),       # Bottom far right
            # Middle row
            (x + 5, y + height // 2),              # Middle left
            (x + width // 2, y + height // 2),     # Middle center
            (x + width - 5, y + height // 2),      # Middle right
            
            # Top row
            (x + 5, y + 5),                        # Top left
            (x + width // 2, y + 5),               # Top center
            (x + width - 5, y + 5),                # Top right
        ]
        # Count how many points are on solid ground
        points_on_platform = 0
        for check_x, check_y in points_to_check:
            # Check square
            if square_rect.collidepoint(check_x, check_y):
                local_x = check_x - square_rect.x
                local_y = check_y - square_rect.y
                if 0 <= local_x < square_mask.get_size()[0] and 0 <= local_y < square_mask.get_size()[1]:
                    if square_mask.get_at((int(local_x), int(local_y))):
                        points_on_platform += 1
                        continue
            # Check triangle
            if triangle_rect.collidepoint(check_x, check_y):
                local_x = check_x - triangle_rect.x
                local_y = check_y - triangle_rect.y
                if 0 <= local_x < triangle_mask.get_size()[0] and 0 <= local_y < triangle_mask.get_size()[1]:
                    if triangle_mask.get_at((int(local_x), int(local_y))):
                        points_on_platform += 1
                        continue
            # Check circle
            if circle_rect.collidepoint(check_x, check_y):
                local_x = check_x - circle_rect.x
                local_y = check_y - circle_rect.y
                if 0 <= local_x < circle_mask.get_size()[0] and 0 <= local_y < circle_mask.get_size()[1]:
                    if circle_mask.get_at((int(local_x), int(local_y))):
                        points_on_platform += 1
                        continue
        # Need at least 2 bottom points OR 4 total points to be safe
        return points_on_platform >= 4
    def is_on_triangle(x, y, w=50, h=100):
        rect = pygame.Rect(x, y, w, h)
        return (check_on_platform(x, y, w, h) and triangle_rect.colliderect(rect))
    def everyone_on_circle(player, bots):
        player_rect = pygame.Rect(player.x, player.y, 50, 100)
        if not player_rect.colliderect(circle_rect):
            return False
        for bot in bots:
            if bot.eliminated:
                continue
            bot_rect = pygame.Rect(bot.x, bot.y, 50, 100)
            if not bot_rect.colliderect(circle_rect):
                return False
        return True
    def zone_is_active(zone_rect):
        if zone_rect == square_rect:
            return square_started
        if zone_rect == triangle_rect:
            return triangle_started
        if zone_rect == circle_rect:
            return circle_started
        return False
    square_duration = 120
    triangle_duration = 120
    circle_duration = 100
    square_button_color = (255, 0, 0)
    square_button_rect = pygame.Rect(640, 360, 10, 10)
    square_start_time = 0
    square_time_left = square_duration
    square_started = False
    triangle_button_color = (255, 0, 0)
    triangle_button_rect = pygame.Rect(1470, 340, 10, 10)
    triangle_started = False
    triangle_start_time = 0
    triangle_time_left = triangle_duration
    wid = 1
    circle_button_color = (0, 0, 0)
    circle_button_rect = pygame.Rect(2280, 355, 10, 10)
    circle_started = False
    circle_start_time = 0
    circle_time_left = circle_duration
    bridge1_x = 640
    bridge2_x = 1260
    BRIDGE1_ORIGINAL_X = bridge1_x
    bridge2_original_x = bridge2_x
    PUSH_FORCE = 80
    PUSH_COOLDOWN = 3050  # milliseconds
    last_push_time = 0
    direction = 1
    font = pygame.font.Font(font_path, 30)
    players = [player1] + bots
    square_elimination_happened = False
    triangle_elimination_happened = False
    circle_elimination_happened = False
    square_completed = False
    triangle_completed = False
    square_pushed_text_color = (255, 0, 0)
    triangle_pushed_text_color = (255, 0, 0)
    circle_pushed_text_color = (255, 0, 0)
    pole1_pickable = False
    pole1_rect = pygame.Rect(620, 240, 20, 130)
    pole1_picked = False
    pole1_used = False
    pole_scaled = pygame.transform.scale(pole_image, (20, 130)).convert_alpha()
    pole_rotated_image = pygame.transform.rotate(pole_scaled, 90)
    pole2_pickable = False
    pole2_rect = pygame.Rect(1440, 240, 20, 130)
    pole2_picked = False
    pole2_used = False
    pole3_pickable = False
    pole3_rect = pygame.Rect(2250, 240, 20, 130)
    pole3_picked = False
    pole3_used = False
    bar_width = 200
    bar_height = 20
    bar_x = game_surface.get_width() // 2 - bar_width // 2
    bar_y = game_surface.get_height() - 60
    win_text = font.render("You WON!", True, (0, 255, 0))
    lose_text = font.render("You Fell...", True, (255, 0, 0))
    pole_text = font.render("Press E to Pickup", True, (255, 0, 0))
    push_label = font.render("SPACE TO PUSH", True, (255, 255, 255))
    sky_won = False
    num_players = 4
    if sprite_id == 1 or sprite_id == 14:
        player1.baby_picked = True
    if player_selected.selected_index == 1 or player_selected.selected_index == 14:
        player1.baby_picked = True
    if player1.baby_picked:
        baby_got = True
    else:
        baby_got = False
    bridge2_done1 = False
    show_decision = False
    sacrifice_button_rect = pygame.Rect(700, 200, 350, 200)
    drop_baby_button_rect = pygame.Rect(230, 200, 350, 200)
    player_fell = False
    font_korean = pygame.font.SysFont("malgungothic", 34)
    font_english = pygame.font.SysFont("Arial", 30)
    voiceline2_played = False
    voiceline3_played = False
    voiceline4_played = False
    voiceline5_played = False
    subtitle_start_time = 0
    subtitle_active = False
    current_subtitle_english = ""
    current_subtitle_korean = ""
    voiceline1_subtitles = [(0, 2, "The game has started.", "게임이 시작되었습니다.")]
    voiceline2_subtitles = [
        (0, 10, "", ""),
        (10, 4, "All players, please proceed to the next round.", "모든 참가자 여러분, 다음 라운드로 이동해 주십시오.")]
    voiceline3_subtitles = [
        (0, 4, "", ""),
        (4, 5, "Please press the button to start the second round.", "2라운드를 시작하려면 버튼을 눌러주세요.")]
    voiceline4_subtitles = [(0, 4, "Please press the button to start the final game.", "마지막 게임을 시작하려면 버튼을 눌러주세요.")]
    voiceline5_subtitles = [
        (0, 2, "", ""),
        (2, 3, "The final game has started.", "결승전이 시작되었습니다.")]
    current_voiceline_subtitles = []
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    exit()
                case pygame.MOUSEBUTTONDOWN:
                    if show_decision:
                        mx, my = scale_mouse_pos(*event.pos)
                        if sacrifice_button_rect.collidepoint(mx, my):
                            baby_got = False
                            player1.baby_picked = False
                            player1.voted = False
                            play_end()
                            from menus import mainmenu
                            return mainmenu()
                        elif drop_baby_button_rect.collidepoint(mx, my):
                            sky_won = True
                            baby_got = False
                            show_decision = False
                case pygame.VIDEORESIZE:
                    handle_resize(event.w, event.h)
                case pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE and is_fullscreen:
                        toggle_fullscreen()
        # Update subtitles
        if subtitle_active:
            current_time = time()
            elapsed = current_time - subtitle_start_time
            # Check which subtitle to show based on elapsed time
            current_subtitle_english = ""
            current_subtitle_korean = ""
            for start, duration, english, korean in current_voiceline_subtitles:
                if start <= elapsed < start + duration:
                    current_subtitle_english = english
                    current_subtitle_korean = korean
                    break
            # Deactivate if all subtitles are done
            if elapsed > max([s[0] + s[1] for s in current_voiceline_subtitles], default=0):
                subtitle_active = False
                current_subtitle_english = ""
                current_subtitle_korean = ""
        if circle_started:
            circle_time_left = circle_duration - (time() - circle_start_time)
        elif triangle_started:
            triangle_time_left = triangle_duration - (time() - triangle_start_time)
        elif square_started:
            square_time_left = square_duration - (time() - square_start_time)
        camera_x = player1.x - game_surface.get_width() // 2
        camera_y = player1.y - game_surface.get_height() // 2
        player1_rect = pygame.Rect(player1.x, player1.y, 50, 100)
        player1_rect1 = pygame.Rect(player1.x, player1.y + 90, 50, 10)
        bridge1_rect = pygame.Rect(bridge1_x, 310, 200, 100)
        bridge2_rect = pygame.Rect(bridge2_x, 310, 400, 100)
        current_time_ticks = pygame.time.get_ticks()
        time_since_push = current_time_ticks - last_push_time
        cooldown_progress = min(time_since_push / PUSH_COOLDOWN, 1.0)
        # Determine bar color
        if cooldown_progress >= 1.0:
            bar_color = (0, 255, 0)  # Green when ready
        else:
            bar_color = (255, 0, 0)  # Red when cooling down
        on_platform = check_on_platform(player1.x, player1.y) or player1_rect.colliderect(bridge1_rect) or player1_rect.colliderect(bridge2_rect)
        if not on_platform:
            player1.eliminated = True
            player_fell = True
        elif player1_rect1.colliderect(square_button_rect) and not square_started:
            square_button_color = (0, 255, 0)
            square_start_time = time()
            sky_voiceline1.play()
            square_started = True
            subtitle_active = True
            subtitle_start_time = time()
            current_voiceline_subtitles = voiceline1_subtitles
        elif player1_rect1.colliderect(triangle_button_rect) and not triangle_started:
            triangle_button_color = (0, 255, 0)
            triangle_start_time = time()
            sky_voiceline1.play()
            triangle_started = True
            subtitle_active = True
            subtitle_start_time = time()
            current_voiceline_subtitles = voiceline1_subtitles
        elif player1_rect1.colliderect(circle_button_rect) and not circle_started:
            circle_button_color = (0, 255, 0)
            wid = 0
            circle_start_time = time()
            sky_voiceline5.play()
            circle_started = True
            subtitle_active = True
            subtitle_start_time = time()
            current_voiceline_subtitles = voiceline5_subtitles
        if circle_started and player1.baby_picked and num_players == 1 and not circle_elimination_happened and bridge2_done1:
            show_decision = True
        elif circle_started and circle_time_left <= 0 and circle_elimination_happened:
            sky_won = True
        elif circle_started and circle_time_left <= 0 and not circle_elimination_happened:
            player1.eliminated = True
        elif triangle_started and triangle_time_left <= 0 and triangle_elimination_happened and not circle_started:
            if not triangle_completed:
                triangle_completed = True
            if bridge2_x < 1600:
                if not voiceline5_played:
                    sky_voiceline2.play()
                    subtitle_active = True
                    subtitle_start_time = time()
                    current_voiceline_subtitles = voiceline2_subtitles
                    voiceline5_played = True
                bridge2_x += 0.5
            else:
                bridge2_done = True
        elif triangle_started and triangle_time_left <= 0 and not triangle_elimination_happened:
            player1.eliminated = True
        elif square_started and square_time_left <= 0 and square_elimination_happened and not triangle_started:
            if not square_completed:
                square_completed = True
            if bridge1_x < 950:
                if not voiceline2_played:
                    sky_voiceline2.play()
                    subtitle_active = True
                    subtitle_start_time = time()
                    current_voiceline_subtitles = voiceline2_subtitles
                    voiceline2_played = True
                bridge1_x += 0.5
            else:
                bridge1_done = True
        elif square_started and square_time_left <= 0 and not square_elimination_happened:
            player1.eliminated = True
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player1.x -= 5
            direction = -1
        elif keys[pygame.K_RIGHT]:
            player1.x += 5
            direction = 1
        if keys[pygame.K_UP]:
            player1.y -= 5
        elif keys[pygame.K_DOWN]:
            player1.y += 5
        if keys[pygame.K_e] and pole1_pickable:
            pole1_picked = True
            pole1_pickable = False
            pole1_rect = pygame.Rect(11620, 240, 20, 130)
        elif keys[pygame.K_e] and pole2_pickable:
            pole2_picked = True
            pole2_pickable = False
            pole2_rect = pygame.Rect(11440, 240, 20, 130)
        elif keys[pygame.K_e] and pole3_pickable:
            pole3_picked = True
            pole3_pickable = False
            pole3_rect = pygame.Rect(12260, 240, 20, 130)
        if hasattr(player1, 'push_velocity'):
            player1.x += player1.push_velocity[0]
            player1.y += player1.push_velocity[1]
            player1.push_velocity[0] *= 0.2
            player1.push_velocity[1] *= 0.2
        if keys[pygame.K_SPACE]:
            now = pygame.time.get_ticks()
            if now - last_push_time > PUSH_COOLDOWN:
                if direction == 1:
                    if pole1_picked and not pole1_used or pole2_picked and not pole2_used or pole3_picked and not pole3_used:
                        player_push_rect = pygame.Rect(player1.x + 45, player1.y, 500, 100)
                    else:
                        player_push_rect = pygame.Rect(player1.x + 45, player1.y, 40, 100)
                elif direction == -1:
                    if pole1_picked and not pole1_used or pole2_picked and not pole2_used or pole3_picked and not pole3_used:
                        player_push_rect = pygame.Rect(player1.x - 45, player1.y, 500, 100)
                    else:
                        player_push_rect = pygame.Rect(player1.x - 45, player1.y, 40, 100)
                last_push_time = now
                for bot in bots:
                    if bot.eliminated:
                        continue
                    bot_rect = pygame.Rect(bot.x, bot.y, 50, 100)
                    if player_push_rect.colliderect(bot_rect):
                        if pole1_picked and not pole1_used:
                            bot.apply_push(3000 * direction, 0)
                            pole1_used = True
                        elif pole2_picked and not pole2_used:
                            bot.apply_push(3000 * direction, 0)
                            pole2_used = True
                        elif pole3_picked and not pole3_used:
                            bot.apply_push(3000 * direction, 0)
                            pole3_used = True
                        else:
                            bot.apply_push(PUSH_FORCE * direction, 0)
        game_surface.fill((0, 0, 0))
        pygame.draw.rect(game_surface, (63, 64, 66), (bridge1_x - camera_x, 310 - camera_y, 200, 100))
        pygame.draw.rect(game_surface, (63, 64, 66), (bridge2_x - camera_x, 310 - camera_y, 400, 100))
        game_surface.blit(square_image, (330 - camera_x, 50 - camera_y))
        game_surface.blit(triangle_image, (1150 - camera_x, 50 - camera_y))
        game_surface.blit(circle_image, (1970 - camera_x, 50 - camera_y))
        pygame.draw.rect(game_surface, square_button_color, (640 - camera_x, 360 - camera_y, 10, 10))
        pygame.draw.polygon(game_surface, triangle_button_color, [(1460 - camera_x, 360 - camera_y), (1465 - camera_x, 350 - camera_y), (1470 - camera_x, 360 - camera_y)])
        pygame.draw.circle(game_surface, circle_button_color, (2280 - camera_x, 360 - camera_y), 5, wid)
        game_surface.blit(player_image, (player1.x - camera_x, player1.y - camera_y))
        game_surface.blit(finalist_suit_image, (player1.x - camera_x, player1.y - camera_y + 41))
        if freeplay == 0:
            game_surface.blit(o_patch_image, (player1.x - camera_x, player1.y - camera_y + 56))
        if player1.baby_picked and baby_got:
            game_surface.blit(baby_image, (player1.x - camera_x, player1.y - camera_y + 61))
        if not pole1_picked:
            game_surface.blit(pole_image, (620 - camera_x, 240 - camera_y))
        elif not pole1_used:
            game_surface.blit(pole_rotated_image, (player1.x - camera_x, player1.y + 30 - camera_y))
        if not pole2_picked:
            game_surface.blit(pole_image, (1440 - camera_x, 240 - camera_y))
        elif not pole2_used:
            game_surface.blit(pole_rotated_image, (player1.x - camera_x, player1.y + 30 - camera_y))
        if not pole3_picked:
            game_surface.blit(pole_image, (2250 - camera_x, 240 - camera_y))
        elif not pole3_used:
            game_surface.blit(pole_rotated_image, (player1.x - camera_x, player1.y + 30 - camera_y))
        players = [player1] + bots
        for bot in bots:
            if not bot.eliminated:
                elimination_in_current_zone = False
                task_completed = False
                button_pressed = False
                bot_zone = bot.get_zone()
                if bot_zone == square_rect:
                    elimination_in_current_zone = square_elimination_happened
                    task_completed = square_completed
                    button_pressed = square_started
                elif bot_zone == triangle_rect:
                    elimination_in_current_zone = triangle_elimination_happened
                    task_completed = triangle_completed
                    button_pressed = triangle_started
                elif bot_zone == circle_rect:
                    elimination_in_current_zone = circle_elimination_happened
                    button_pressed = circle_started
                bot.update(players, elimination_in_current_zone, task_completed, button_pressed)
                bot_rect = pygame.Rect(bot.x, bot.y, 50, 100)    
                bot_on_platform = check_on_platform(bot.x, bot.y, 50, 100) or bot_rect.colliderect(bridge1_rect) or bot_rect.colliderect(bridge2_rect)
                if not bot_on_platform:
                    if zone_is_active(bot_zone):
                        if bot_zone == square_rect:
                            square_elimination_happened = True
                        elif bot_zone == triangle_rect:
                            triangle_elimination_happened = True
                        elif bot_zone == circle_rect:
                            circle_elimination_happened = True
                    bot.eliminated = True
                    num_players -= 1
                if not bot.moving_to_next_zone:
                    if circle_started:
                        bot.target = "circle"
                    elif triangle_started:
                        bot.target = "triangle"
                    else:
                        bot.target = "square"
                game_surface.blit(bot.image, (bot.x - camera_x, bot.y - camera_y))
                game_surface.blit(finalist_suit_image, (bot.x - camera_x, bot.y - camera_y + 41))
                if freeplay == 0:
                    game_surface.blit(o_patch_image, (bot.x - camera_x, bot.y - camera_y + 56))
        all_on_triangle = True
        if not is_on_triangle(player1.x, player1.y):
            all_on_triangle = False
        for bot in bots:
            if bot.eliminated:
                continue
            if not is_on_triangle(bot.x, bot.y):
                all_on_triangle = False
                break
        if all_on_triangle:
            if bridge1_x > BRIDGE1_ORIGINAL_X:
                if not voiceline3_played:
                    sky_voiceline3.play()
                    subtitle_active = True
                    subtitle_start_time = time()
                    current_voiceline_subtitles = voiceline3_subtitles
                    voiceline3_played = True
                bridge1_x -= 1
                if bridge1_x < BRIDGE1_ORIGINAL_X:
                    bridge1_x = BRIDGE1_ORIGINAL_X
        if everyone_on_circle(player1, bots):
            if bridge2_x > bridge2_original_x:
                bridge2_x -= 1
            else:
                if not voiceline4_played:
                    sky_voiceline4.play()
                    subtitle_active = True
                    subtitle_start_time = time()
                    current_voiceline_subtitles = voiceline4_subtitles
                    voiceline4_played = True
                bridge2_done1 = True
        filled_width = int(bar_width * cooldown_progress)
        pygame.draw.rect(game_surface, bar_color, (bar_x, bar_y, filled_width, bar_height))
        pygame.draw.rect(game_surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        game_surface.blit(push_label, (bar_x + bar_width // 2 - push_label.get_width() // 2, bar_y - 35))
        minut = int(square_time_left) // 60
        sec = int(square_time_left) % 60
        time_text = font.render(f"{minut}:{sec:02}", True, (255, 0, 0))
        if square_time_left > 0 and square_started:
            game_surface.blit(time_text, (game_surface.get_width() // 2 - time_text.get_width() // 2, 10))
            pushed_text = font.render("0/1 Pushed OFF", True, square_pushed_text_color)
            if square_elimination_happened:
                square_pushed_text_color = (0, 255, 0)
                pushed_text = font.render("1/1 Pushed OFF", True, square_pushed_text_color)
            game_surface.blit(pushed_text, (game_surface.get_width() // 2 - pushed_text.get_width() // 2, 50))
        elif triangle_time_left > 0 and triangle_started:
            minut = int(triangle_time_left) // 60
            sec = int(triangle_time_left) % 60
            time_text = font.render(f"{minut}:{sec:02}", True, (255, 0, 0))
            game_surface.blit(time_text, (game_surface.get_width() // 2 - time_text.get_width() // 2, 10))
            pushed_text = font.render("0/1 Pushed OFF", True, triangle_pushed_text_color)
            if triangle_elimination_happened:
                triangle_pushed_text_color = (0, 255, 0)
                pushed_text = font.render("1/1 Pushed OFF", True, triangle_pushed_text_color)
            game_surface.blit(pushed_text, (game_surface.get_width() // 2 - pushed_text.get_width() // 2, 50))
        elif circle_time_left > 0 and circle_started:
            minut = int(circle_time_left) // 60
            sec = int(circle_time_left) % 60
            time_text = font.render(f"{minut}:{sec:02}", True, (255, 0, 0))
            game_surface.blit(time_text, (game_surface.get_width() // 2 - time_text.get_width() // 2, 10))
            pushed_text = font.render("0/1 Pushed OFF", True, circle_pushed_text_color)
            if circle_elimination_happened:
                circle_pushed_text_color = (0, 255, 0)
                pushed_text = font.render("1/1 Pushed OFF", True, circle_pushed_text_color)
            game_surface.blit(pushed_text, (game_surface.get_width() // 2 - pushed_text.get_width() // 2, 50))
        if player1_rect.colliderect(pole1_rect):
            pole1_pickable = True
            game_surface.blit(pole_text, (game_surface.get_width() // 2 - pole_text.get_width() // 2, 90))
        elif player1_rect.colliderect(pole2_rect):
            pole2_pickable = True
            game_surface.blit(pole_text, (game_surface.get_width() // 2 - pole_text.get_width() // 2, 90))
        elif player1_rect.colliderect(pole3_rect):
            pole3_pickable = True
            game_surface.blit(pole_text, (game_surface.get_width() // 2 - pole_text.get_width() // 2, 90))
        else:
            pole1_pickable = False
            pole2_pickable = False
            pole3_pickable = False
        if subtitle_active and current_subtitle_english:
            eng_surface = font_english.render(current_subtitle_english, True, (0, 255, 0))
            kor_surface = font_korean.render(current_subtitle_korean, True, (255, 255, 255))
            game_surface.blit(kor_surface, (game_surface.get_width()//2 - kor_surface.get_width()//2, 520))
            game_surface.blit(eng_surface, (game_surface.get_width()//2 - eng_surface.get_width()//2, 560))
        if player1.eliminated:
            player1.baby_picked = False
            from menus import mainmenu
            if not player_fell:
                lose_text = font.render("You Lost...", 1, (255, 0, 0))
            game_surface.blit(lose_text, (game_surface.get_width() // 2 - lose_text.get_width() // 2, 600))
            render_to_screen()
            sleep(3)
            player1.voted = False
            return mainmenu()
        elif sky_won:
            player1.baby_picked = False
            if not baby_got:
                game_surface.blit(player_image, (player1.x - camera_x, player1.y - camera_y))
                game_surface.blit(finalist_suit_image, (player1.x - camera_x, player1.y - camera_y + 41))
                if freeplay == 0:
                    game_surface.blit(o_patch_image, (player1.x - camera_x, player1.y - camera_y + 56))
            from menus import mainmenu
            game_surface.blit(win_text, (game_surface.get_width() // 2 - win_text.get_width() // 2, 600))
            render_to_screen()
            sleep(3)
            player1.voted = False
            return mainmenu()
        elif show_decision:
            game_surface.blit(sacrifice_image, (700, 200))
            game_surface.blit(drop_baby_image, (230, 200))
        render_to_screen()