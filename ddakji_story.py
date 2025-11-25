import pygame
from main import font_path
from assets import blue_ddakji_image, red_ddakji_image, maintheme
from player import player1
from sys import exit
from intro import play_intro_and_show_subtitles
from resize import handle_resize, toggle_fullscreen, is_fullscreen, render_to_screen, game_surface
def story_ddakji(ddakji_story=0):
    play_intro_and_show_subtitles(9)
    maintheme.play(-1)
    font2 = pygame.font.Font(font_path, 40)
    power_level = 0
    max_power = 100
    power_speed = 2
    space_held = False
    first_fail_played = False
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BAR_WIDTH = 40
    BAR_HEIGHT = 300
    BAR_X = 920
    BAR_Y = 300
    blue_ddakji_image1 = pygame.transform.scale(blue_ddakji_image, (100, 100))
    red_ddakji_image1 = pygame.transform.scale(red_ddakji_image, (100, 100))
    clock = pygame.time.Clock()
    while True:
        clock.tick(25)
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    exit()
                case pygame.VIDEORESIZE:
                    handle_resize(event.w, event.h)
                case pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        space_held = True
                    elif event.key == pygame.K_F11:
                        toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE and is_fullscreen:
                        toggle_fullscreen()
                case pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        space_held = False
                        if power_level >= 70 and power_level <= 80:
                            player1.ddakji_flipped = True
                        else:
                            if first_fail_played:
                                play_intro_and_show_subtitles(11)
                            elif not first_fail_played:
                                play_intro_and_show_subtitles(10)
                                first_fail_played = True
                        # Reset power after action
                        power_level = 0
        if space_held:
            power_level = min(max_power, power_level + power_speed)
        fill_height = int((power_level / max_power) * BAR_HEIGHT)
        pygame.draw.rect(game_surface, WHITE, (BAR_X, BAR_Y, BAR_WIDTH, BAR_HEIGHT), 2)
        if fill_height > 0:
            pygame.draw.rect(game_surface, RED, (BAR_X, BAR_Y + BAR_HEIGHT - fill_height, BAR_WIDTH, fill_height))
        if player1.ddakji_flipped:
            maintheme.stop()
            play_intro_and_show_subtitles(12)
            from lobby import waiting
            match ddakji_story:
                case 0:
                    return waiting(0)
                case 1:
                    return waiting(1)
        game_surface.blit(red_ddakji_image1, (620, 500))
        game_surface.blit(blue_ddakji_image1, (620, 100))
        space_surface = font2.render("Hold Space to fill Strength Bar", True, (255, 0, 0))
        game_surface.blit(space_surface, (game_surface.get_width()//2 - space_surface.get_width()//2, 660))
        render_to_screen()