import pygame
from assets import marbles_theme, background_marbles1_image
from player import player1, reset_player
from intro import play_intro_and_show_subtitles
from resize import handle_resize, toggle_fullscreen, is_fullscreen, render_to_screen, scale_mouse_pos, game_surface
from random import choice, randint
from main import font_path
from sys import exit
from time import sleep
from button import draw_button
from player import Player
def marbles(freeplay=0):
    reset_player()
    play_intro_and_show_subtitles(4)
    marbles_theme.play(-1)
    bet_buttons = []
    for i in range(1, 10):
        x = 100 + ((i - 1) % 5) * 90
        y = 400 if i <= 5 else 480
        bet_buttons.append((pygame.Rect(x, y, 80, 60), str(i)))
    odd_button = pygame.Rect(700, 400, 150, 60)
    even_button = pygame.Rect(700, 480, 150, 60)
    font = pygame.font.Font(font_path, 40)
    large_font = pygame.font.Font(font_path, 80)
    clock = pygame.time.Clock()
    player1.marbles = 10
    player2 = Player(0, 0)
    player2.marbles = 10
    player2.marbles_guess = None
    player2.marbles_bet = None
    bet = None
    guess = None
    submitted_bet = False
    submitted_guess = False
    result_message = ""
    showing_result = False
    result_timer = 0
    while True:
        clock.tick(10)
        game_surface.blit(background_marbles1_image, (0, 0))
        if player1.eliminated:
            text = large_font.render("You lost!", True, (255, 0, 0))
            game_surface.blit(text, ((game_surface.get_width() - text.get_width()) // 2, (game_surface.get_height() - text.get_height()) // 2))
            render_to_screen()
            sleep(5)
            marbles_theme.stop()
            from menus import mainmenu
            return mainmenu()
        elif player1.marbles_won:
            text = large_font.render("You WON!", True, (0, 255, 0))
            game_surface.blit(text, ((game_surface.get_width() - text.get_width()) // 2, (game_surface.get_height() - text.get_height()) // 2))
            render_to_screen()
            sleep(5)
            match freeplay:
                case 0:
                    from lobby import lobby
                    lobby("Glass Stepping Stones is Next!", duration=20, lights=0)
                    from glassbridge import glass_bridge
                    return glass_bridge(0)
                case 1:
                    marbles_theme.stop()
                    from menus import mainmenu
                    return mainmenu()
        game_surface.blit(font.render(f"Your marbles: {player1.marbles}/20", True, (255, 255, 0)), (100, 100))
        # Display instructions and state
        if not submitted_bet:
            game_surface.blit(font.render("Enter your bet (1-9)", True, (255, 255, 255)), (100, 160))
        elif not submitted_guess:
            game_surface.blit(font.render("Your turn: Odd or Even", True, (255, 255, 255)), (100, 220))
        if bet is not None:
            game_surface.blit(font.render(f"Your bet: {bet}", True, (255, 255, 255)), (100, 280))
        if guess:
            game_surface.blit(font.render(f"Your guess: {guess}", True, (255, 255, 255)), (100, 320))
        if result_message:
            game_surface.blit(font.render(result_message, True, (0, 255, 0)), (100, 360))
        # Show guess buttons if it's player's turn
        elif not submitted_guess and player1.marbles_turn:
            draw_button(odd_button, "Odd", font)
            draw_button(even_button, "Even", font)
        render_to_screen()
        # Handle input
        for event in pygame.event.get():
            match event.type: 
                case pygame.QUIT:
                    exit()
                case pygame.VIDEORESIZE:
                    handle_resize(event.w, event.h)
                case pygame.MOUSEBUTTONDOWN:
                    mx, my = scale_mouse_pos(*event.pos)
                    if submitted_bet and not submitted_guess and player1.marbles_turn:
                        if odd_button.collidepoint(mx, my):
                            guess = "odd"
                        elif even_button.collidepoint(mx, my):
                            guess = "even"
                        if guess:
                            player1.marbles_guess = guess
                            submitted_guess = True
                case pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE and is_fullscreen:
                        toggle_fullscreen()
                    elif not submitted_bet and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                        bet = int(event.unicode)
                        if bet <= player1.marbles:
                            player1.marbles_bet = bet
                            submitted_bet = True
                            player1.marbles_turn = True
                            player2.marbles_bet = randint(1, min(player2.marbles, 9))
        # After both player and bot bet + guess
        if submitted_bet and submitted_guess and not showing_result:
            # Bot guess logic (random)
            player2.marbles_guess = choice(["odd", "even"])
            # Evaluate turn
            correct = (player2.marbles_bet % 2 == 1 and player1.marbles_guess == "odd") or \
                      (player2.marbles_bet % 2 == 0 and player1.marbles_guess == "even")
            if correct:
                player1.marbles += player1.marbles_bet
                player2.marbles -= player1.marbles_bet
                result_message = f"You guessed right! +{player1.marbles_bet} marbles"
            else:
                player1.marbles -= player2.marbles_bet
                player2.marbles += player2.marbles_bet
                result_message = f"You guessed wrong! -{player2.marbles_bet} marbles"
            showing_result = True
            result_timer = pygame.time.get_ticks()
            # Win/loss check
            if player1.marbles >= 20:
                player1.marbles = 20
                player1.marbles_won = True
            elif player1.marbles <= 0:
                player1.marbles = 0
                player1.eliminated = True
            if player2.marbles <= 0:
                player2.marbles = 0
                player1.marbles_won = True
        # Show result for 3 seconds
        if showing_result:
            game_surface.blit(font.render(result_message, True, (0, 255, 0)), (100, 560))
            render_to_screen()
            if pygame.time.get_ticks() - result_timer > 3000:
                showing_result = False
                submitted_bet = False
                submitted_guess = False
                result_message = ""
                bet = None
                guess = None
                player1.marbles_guess = None
                player1.marbles_bet = None
                player2.marbles_guess = None
                player2.marbles_bet = None