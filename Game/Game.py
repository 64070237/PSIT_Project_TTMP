"""This is the main of the game"""
import pygame.font

from Sprite import *

# Screen settings and display
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Platform')

# Set Frame rate
clock = pygame.time.Clock()

# Defined player action variables
move_left = False
move_right = False
shoot = False
grenade = False
grenade_thrown = False

font = pygame.font.SysFont('Futura', 30)

# Background image
sky_image = pygame.image.load('img/Background/Sky.png').convert_alpha()
sky_image = pygame.transform.scale(sky_image, (int(sky_image.get_width() * BG_SCALE),
                                               int(sky_image.get_height()) * BG_SCALE))
mountain_image = pygame.image.load('img/Background/Mountain.png').convert_alpha()
mountain_image = pygame.transform.scale(mountain_image, (int(mountain_image.get_width() * BG_SCALE),
                                                         int(mountain_image.get_height()) * BG_SCALE))
forest_image_1 = pygame.image.load('img/Background/Forest small.png').convert_alpha()
forest_image_1 = pygame.transform.scale(forest_image_1, (int(forest_image_1.get_width() * BG_SCALE),
                                                         int(forest_image_1.get_height()) * BG_SCALE))
forest_image_2 = pygame.image.load('img/Background/Forest small 2.png').convert_alpha()
forest_image_2 = pygame.transform.scale(forest_image_2, (int(forest_image_2.get_width() * BG_SCALE),
                                                         int(forest_image_2.get_height()) * BG_SCALE))
field_image = pygame.image.load('img/Background/Field.png').convert_alpha()
field_image = pygame.transform.scale(field_image, (int(field_image.get_width() * BG_SCALE),
                                                   int(field_image.get_height()) * BG_SCALE))


def draw_text(text, font, text_col, x, y):
    """Draw Text"""
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    """Screen BG Woo!!!"""
    screen.blit(sky_image, (0, 0))
    screen.blit(mountain_image, (0, 120))
    screen.blit(forest_image_2, (0, 150))
    screen.blit(forest_image_1, (0, 160))
    screen.blit(field_image, (0, 210))
    pygame.draw.line(screen, RED, (0, 500), (SCREEN_WIDTH, 500))


# Run the game YAY!!!
run = True
while run:

    clock.tick(FPS)

    draw_bg()
    # show health bar
    draw_text(f'Health: {player.health} / {player.max_health}', font, BLACK, 10, 30)
    # health_bar.draw(player.health)

    # show ammo
    draw_text(f'Ammo: {player.ammo}', font, BLACK, 10, 60)
    # for x in range(player.ammo):
    # screen.blit(player.ammo_type, (85 + (x * 15), 62))

    # show grenade
    draw_text(f'Grenade: {player.grenades}', font, BLACK, 10, 90)
    # for x in range(player.grenades):
    # screen.blit(player.grenades_type, (100 + (x * 15), 76))

    player.update()
    player.draw()

    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()

    # Update and draw group
    bullet_group.update()
    grenade_group.update()
    explosion_group.update()
    item_group.update()

    bullet_group.draw(screen)
    grenade_group.draw(screen)
    explosion_group.draw(screen)
    item_group.draw(screen)

    if player.alive:
        # Update player actions
        if shoot:
            player.shoot()
        elif grenade and not grenade_thrown and player.grenades > 0:
            grenade = Grenade(
                player.rect.centerx + (0.7 * player.rect.size[0] * player.direction),
                player.rect.top, grenades,
                player.direction)
            grenade_group.add(grenade)
            player.grenades -= 1
            grenade_thrown = True
        if player.in_air:
            player.update_action(2)  # 2 : Jump
        elif move_left or move_right:
            player.update_action(1)  # 1 : Run
        else:
            player.update_action(0)  # 0 : Idle
        player.move(move_left, move_right)

    for event in pygame.event.get():
        # Quit Game Event
        if event.type == pygame.QUIT:
            run = False

        # Checking keys press or not?
        # Pressing keys...
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                move_left = True
            if event.key == pygame.K_d:
                move_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True

        # Releasing keys...
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                move_left = False
            if event.key == pygame.K_d:
                move_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    pygame.display.update()

pygame.quit()
