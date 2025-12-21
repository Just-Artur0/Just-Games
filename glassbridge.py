import pygame
from assets import background_glassbridge_image, glass_image, marbles_theme, glassbridge_theme, glass_shatter, glassbridge_collapse, o_patch_image
from player import player_image, all_player_images, reset_player, player1
from intro import play_intro_and_show_subtitles
from resize import handle_resize, toggle_fullscreen, is_fullscreen, render_to_screen, game_surface, scale_mouse_pos
from main import font_path
from sys import exit
from random import choice, randint, shuffle
from time import time
from button import draw_button
import player_selected
def glass_bridge(freeplay=0):
    global player_image
    reset_player()
    marbles_theme.stop()
    play_intro_and_show_subtitles(5)
    if player_selected.selected_index is None:
        if freeplay == 1:
            sprite_id = randint(0, 22)
            player_image = all_player_images[sprite_id]
    else:
        player_image = all_player_images[player_selected.selected_index]
    glassbridge_theme.play(-1)
    font = pygame.font.Font(font_path, 40)
    top_button = pygame.Rect(800, 500, 170, 60)
    bottom_button = pygame.Rect(800, 580, 170, 60)
    clock = pygame.time.Clock()
    glass_shatter_channel = pygame.mixer.Channel(5)
    glassbridge_collapse_channel = pygame.mixer.Channel(6)
    spacing = 150
    steps = 7
    x_start = 150
    y_center = 400
    panel_gap = 100
    fall_y = None
    bridge_collapse = False
    glass_shattered = False
    collapse_index = 0
    collapse_timer = time()
    collapse_start_time = None
    glassbridge_collapsing = False
    glassbridge_start_time = time()
    GLASSBRIDGE_DURATION = 480
    glassbridge_time_left = GLASSBRIDGE_DURATION
    DEATH_DURATION = 3
    death_time_left = DEATH_DURATION
    death_start_time = None
    death_started = False
    glass_bridge_sequence = [choice([0, 1]) for _ in range(steps)]
    broken_panels = []
    successful_moves = {}  # step: side mapping
    failed_moves = {}      # step -> wrong side(s)
    class Bot:
        def __init__(self, bot_id):
            self.bot_id = bot_id
            self.sprite_id = randint(0, 22)
            self.glass_step = 0
            self.glass_side = 0
            self.glass_choice = None
            self.glass_ready = False
            self.eliminated = False
            self.glass_win = False
            self.fall_y = None
            self.move_timer = 0
            self.choice_delay = randint(80, 140)  # 1-3 seconds at 20fps
            self.following = False  # Track if bot is following a successful move 
        def update(self, is_current_turn=False):
            if self.eliminated or self.glass_win or not is_current_turn:
                return
            # Bot makes choice after delay
            self.move_timer += 1
            if self.move_timer >= self.choice_delay and not self.glass_ready:
                if self.glass_step in successful_moves:
                    # Follow known good move
                    self.glass_choice = successful_moves[self.glass_step]
                    self.following = True
                else:
                    # Avoid known failed sides
                    possible_choices = [0, 1]
                    if self.glass_step in failed_moves:
                        for bad in failed_moves[self.glass_step]:
                            if bad in possible_choices:
                                possible_choices.remove(bad)
                    if possible_choices:
                        self.glass_choice = choice(possible_choices)
                    else:
                        # Safety fallback (shouldn’t happen unless both sides failed)
                        self.glass_choice = choice([0, 1])
                    self.following = False
                self.glass_ready = True
        def process_step(self, glass_bridge_sequence, broken_panels, successful_moves):
            if self.glass_ready and not self.eliminated and not self.glass_win:
                self.glass_ready = False
                if self.glass_step < len(glass_bridge_sequence):
                    correct = glass_bridge_sequence[self.glass_step]
                    if self.glass_choice == correct:
                        self.glass_side = self.glass_choice
                        # Record this as a successful move for other bots to follow
                        successful_moves[self.glass_step] = self.glass_choice
                        self.glass_step += 1
                        if self.glass_step == len(glass_bridge_sequence):
                            self.glass_win = True
                    else:
                        self.glass_side = self.glass_choice
                        broken_panels.append((self.glass_step, self.glass_choice))
                        self.eliminated = True
                        self.fall_y = y_center - panel_gap // 2 if self.glass_choice == 0 else y_center + panel_gap // 2

                        # Record this side as failed so others won’t try it
                        if self.glass_step not in failed_moves:
                            failed_moves[self.glass_step] = set()
                        failed_moves[self.glass_step].add(self.glass_choice)
                # Reset for next choice
                self.glass_choice = None
                self.move_timer = 0
                self.choice_delay = randint(80, 140)
                return True  # Indicates move was made
            return False  # No move made
        def advance_to_current_step(self, target_step, successful_moves):
            """Advance bot through all known successful moves up to target step"""
            while self.glass_step < target_step and self.glass_step in successful_moves:
                self.glass_side = successful_moves[self.glass_step]
                self.glass_step += 1
                if self.glass_step == len(glass_bridge_sequence):
                    self.glass_win = True
                    break
    # Create bots and determine turn order
    bots = [Bot(i) for i in range(6)]
    all_players = [player1] + bots
    turn_order = all_players.copy()
    shuffle(turn_order)  # Random turn order
    current_turn_index = 0
    current_player = turn_order[current_turn_index]
    def get_next_alive_player():
        nonlocal current_turn_index, current_player
        start_index = current_turn_index
        while True:
            current_turn_index = (current_turn_index + 1) % len(turn_order)
            current_player = turn_order[current_turn_index]
            if not current_player.eliminated and not current_player.glass_win:
                break
            # If we've checked everyone, no one is alive
            if current_turn_index == start_index:
                current_player = None
                break
    def advance_all_bots_to_step(target_step):
        """Advance all non-eliminated bots through known successful moves"""
        for bot in bots:
            if not bot.eliminated and not bot.glass_win:
                bot.advance_to_current_step(target_step, successful_moves)
    while True:
        clock.tick(20)
        game_surface.blit(background_glassbridge_image, (0, 0))
        for bot in bots:
            bot.update(is_current_turn=(bot is current_player))
        if not glass_shattered and player1.eliminated:
            glass_shatter_channel.play(glass_shatter)
            glass_shattered = True
        if player1.eliminated and fall_y is None:
            fall_y = player1.y
        elapsed = time() - glassbridge_start_time
        glassbridge_time_left = max(-10, GLASSBRIDGE_DURATION - int(elapsed))
        if glassbridge_time_left <= 0 and not bridge_collapse:
            glassbridge_collapse_channel.play(glassbridge_collapse)
            bridge_collapse = True
        if death_start_time is not None:
            elapsed2 = time() - death_start_time
            death_time_left = max(0, DEATH_DURATION - int(elapsed2))
        if glassbridge_time_left <= 0:
            if not glassbridge_collapsing:
                if collapse_start_time is None:
                    collapse_start_time = time()
                elif time() - collapse_start_time >= 4:
                    glassbridge_collapsing = True
                    collapse_index = 0
                    collapse_timer = time()
            elif time() - collapse_timer >= 0.3:
                step = collapse_index // 2
                side = collapse_index % 2
                if (step, side) not in broken_panels:
                    broken_panels.append((step, side))
                collapse_index += 1
                collapse_timer = time()
        if current_player is not None:
            if current_player == player1:
                # Player turn logic
                if player1.glass_ready and not player1.eliminated and not player1.glass_win:
                    player1.glass_ready = False
                    if player1.glass_step < len(glass_bridge_sequence):
                        correct = glass_bridge_sequence[player1.glass_step]
                        if player1.glass_choice == correct:
                            player1.glass_side = player1.glass_choice
                            # Record successful move for bots to follow
                            successful_moves[player1.glass_step] = player1.glass_choice
                            player1.glass_step += 1
                            # Advance all bots to this step if they're behind
                            advance_all_bots_to_step(player1.glass_step)
                            if player1.glass_step == len(glass_bridge_sequence):
                                player1.glass_win = True
                        else:
                            player1.glass_side = player1.glass_choice
                            broken_panels.append((player1.glass_step, player1.glass_choice))
                            player1.eliminated = True
                            if player1.glass_step not in failed_moves:
                                failed_moves[player1.glass_step] = set()
                            failed_moves[player1.glass_step].add(player1.glass_choice)
                    player1.glass_choice = None
                    get_next_alive_player()
            else:
                # Bot turn logic
                if current_player.process_step(glass_bridge_sequence, broken_panels, successful_moves):
                    get_next_alive_player()
        # Draw glass bridge
        for i in range(steps):
            x = x_start + i * spacing
            top_y = y_center - panel_gap // 2 - glass_image.get_height() // 2
            bot_y = y_center + panel_gap // 2 - glass_image.get_height() // 2
            if (i, 0) not in broken_panels:
                game_surface.blit(glass_image, (x, top_y))
            if (i, 1) not in broken_panels:
                game_surface.blit(glass_image, (x, bot_y))
        # Draw player
        if player1.glass_win:
            my_x = (x_start - spacing + player1.glass_step * spacing) + 150
            my_y = (y_center - panel_gap // 2 if player1.glass_side == 0 else y_center + panel_gap // 2) - 50
        else:
            my_x = x_start - spacing + player1.glass_step * spacing
            my_y = y_center - panel_gap // 2 if player1.glass_side == 0 else y_center + panel_gap // 2
        my_y -= player_image.get_height() // 2
        if fall_y is not None:
            fall_y += 15
            game_surface.blit(player_image, (my_x + spacing, fall_y))
            if freeplay == 0:
                game_surface.blit(o_patch_image, (my_x + spacing, fall_y + 56))
        elif not player1.eliminated:
            # Highlight if it's player's turn
            if current_player == player1:
                highlight = pygame.Surface((player_image.get_width() + 10, player_image.get_height() + 10))
                highlight.set_alpha(100)
                highlight.fill((0, 255, 0))
                game_surface.blit(highlight, (my_x - 5, my_y - 5))
            game_surface.blit(player_image, (my_x, my_y))
            if freeplay == 0:
                game_surface.blit(o_patch_image, (my_x, my_y + 56))
        game_surface.blit(font.render(f"Step: {player1.glass_step}/{steps}", True, (255, 255, 255)), (50, 50))
        if current_player == player1:
            turn_text = "Your Turn!"
            color = (0, 255, 0)
        elif current_player is not None:
            turn_text = f"Bot {current_player.bot_id + 1}'s Turn"
            color = (255, 255, 0)
        game_surface.blit(font.render(turn_text, True, color), (50, 100))
        if player1.eliminated:
            if not death_started:
                death_start_time = time()
                death_started = True
            game_surface.blit(font.render("You Fell!", True, (255, 0, 0)), (450, 600))
        if death_time_left <= 0:
            from menus import mainmenu
            player1.voted = False
            glassbridge_theme.stop()
            return mainmenu()
        elif player1.glass_win:
            game_surface.blit(font.render("You made it!", True, (0, 255, 0)), (500, 600))
        minutes = max(0, glassbridge_time_left) // 60
        seconds = max(0, glassbridge_time_left) % 60
        timer_text = f"{int(minutes):02}:{int(seconds):02}"
        timer_surface = pygame.font.Font(font_path, 60).render(timer_text, True, (255, 0, 0))
        game_surface.blit(timer_surface, (game_surface.get_width() // 2 - timer_surface.get_width() // 2, 20))
        if not player1.eliminated and not player1.glass_win:
            draw_button(top_button, "Top", font)
            draw_button(bottom_button, "Bottom", font)
        for bot in bots:
            if bot.glass_win:
                bot_x = (x_start - spacing + bot.glass_step * spacing) + 150
                bot_y = (y_center - panel_gap // 2 if bot.glass_side == 0 else y_center + panel_gap // 2) - 50
            else:
                bot_x = x_start - spacing + bot.glass_step * spacing
                bot_y = y_center - panel_gap // 2 if bot.glass_side == 0 else y_center + panel_gap // 2
            bot_y -= all_player_images[bot.sprite_id].get_height() // 2
            if bot.fall_y is not None:
                bot.fall_y += 15
                game_surface.blit(all_player_images[bot.sprite_id], (bot_x + spacing, bot.fall_y))
            elif not bot.eliminated:
                # Highlight current turn
                if current_player == bot:
                    highlight = pygame.Surface((all_player_images[bot.sprite_id].get_width() + 10, all_player_images[bot.sprite_id].get_height() + 10))
                    highlight.set_alpha(100)
                    highlight.fill((255, 255, 0))
                    game_surface.blit(highlight, (bot_x - 5, bot_y - 5))
                game_surface.blit(all_player_images[bot.sprite_id], (bot_x, bot_y))
                if freeplay == 0:
                    game_surface.blit(o_patch_image, (bot_x, bot_y + 56))
        render_to_screen()
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
            if event.type == pygame.MOUSEBUTTONDOWN and not player1.eliminated and not player1.glass_win:
                mx, my = scale_mouse_pos(*event.pos)
                if top_button.collidepoint(mx, my):
                    player1.glass_choice = 0
                    player1.glass_ready = True
                elif bottom_button.collidepoint(mx, my):
                    player1.glass_choice = 1
                    player1.glass_ready = True
        if glassbridge_time_left == -10:
            from menus import mainmenu
            glassbridge_theme.stop()
            if not player1.eliminated:
                match freeplay:
                    case 0:
                        from lobby import lobby
                        lobby("Squid Game is Next!", duration=20, lights=0)
                        from squidgame import squidgame
                        return squidgame(0)
                    case 1:
                        return mainmenu()
            player1.voted = False
            return mainmenu()