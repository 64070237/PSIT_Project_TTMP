"""This is all sprite"""
import pygame
import os
import random
from Config import *

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


# Player class: adjust how player will be in the game
class Character(pygame.sprite.Sprite):
    """Character Load For PLayer and Enemies"""

    # Load player image and position!?
    def __init__(self, char_type, health, x, y, scale, speed, ammo, ammo_type, grenade, grenades_type):
        """init"""
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.ammo_type = ammo_type
        self.start_ammo = ammo
        self.shoot_cool_down = 0
        self.grenades = grenade
        self.grenades_type = grenades_type
        self.health = health
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # Create AI specific variable
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 250, 20)
        self.idling = False
        self.idling_counter = 0

        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # Reset temporary list of image
            temp_list = []
            # Count number of files in folders
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale),
                                                   int(img.get_height()) * scale))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        """Update"""
        self.update_animation()
        self.check_alive()
        # Update cool down
        if self.shoot_cool_down > 0:
            self.shoot_cool_down -= 1

    # Moving the player!?
    def move(self, moving_left, moving_right):
        """Movement For Character"""
        # Reset movement
        dx = 0
        dy = 0

        # assign movement variable
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Jump
        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Check collision with floor
        if self.rect.bottom + dy > 500:
            dy = 500 - self.rect.bottom
            self.in_air = False

        # Update rect position
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        """Shoot"""
        if self.shoot_cool_down == 0 and self.ammo > 0:
            self.shoot_cool_down = BULLET_COOL_DOWN
            bullet = Bullet(self.rect.centerx
                            + (0.8 * self.rect.size[0] * self.direction),
                            self.rect.centery + 7, self.ammo_type, self.direction)
            bullet_group.add(bullet)
            # Reduce ammo
            self.ammo -= 1

    def ai(self):
        """For AI method"""
        if self.alive and player.alive:
            if not self.idling and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 500

            # check if the ai in neat the player
            if self.vision.colliderect(player.rect):
                # stop running and shoot player
                self.update_action(0)
                # shoot
                self.shoot()
            else:
                if not self.idling:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1

                    if self.move_counter > 100:
                        self.direction *= -1
                        self.move_counter *= -1

                    # update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 125 * self.direction, self.rect.centery)
                    # pygame.draw.rect(screen, RED, self.vision)
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

    def update_animation(self):
        """We will have animation now"""
        # Update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # Check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOL_DOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        """check if the new action is different to the previous one"""
        if new_action != self.action:
            self.action = new_action
            # Update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        """Check If player/Enemies Dies or not"""
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    # Draw player on the screen!!!
    def draw(self):
        """Yes, Draw Player on the screen"""
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


# Load Bullet image
bullet = pygame.image.load('img/Variable/Bullet/bullet.png').convert_alpha()
arrow = pygame.image.load('img/Variable/Bullet/Arrow.png').convert_alpha()

# Load Grenade image
grenades = pygame.image.load('img/Variable/Grenade/0.png').convert_alpha()

# Load Item image
health_potion_img = pygame.image.load('img/Variable/Item/Health potion.png').convert_alpha()
mana_potion_img = pygame.image.load('img/Variable/Item/Mana potion.png').convert_alpha()
charge_potion_img = pygame.image.load('img/Variable/Item/Charge potion.png').convert_alpha()
items = {
    'Health': health_potion_img,
    'Mana': mana_potion_img,
    'Grenade': charge_potion_img
}


class Health_bar:
    def __init__(self, x, y, health, max_health):
        """Health Bar"""
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
        self.red_bar = pygame.image.load('img/Variable/Bar/Red_bar.png')
        self.green_bar = pygame.image.load('img/Variable/Bar/Green_bar.png')

    def draw(self, health):
        # Update with new health
        self.health = health
        # Calculate health ratio
        pygame.draw.rect(screen, BLACK, (self.x + 2, self.y + 14, 206, 30))
        for x in range(player.max_health):
            screen.blit(self.red_bar, (90 + (x * 2), 25))
        for x in range(player.health):
            screen.blit(self.green_bar, (90 + (x * 2), 25))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, ammo_type, direction):
        """Shooting"""
        pygame.sprite.Sprite.__init__(self)
        self.speed = 5
        self.image = ammo_type
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        """Update Bullet Animation"""
        # Move Bullet
        self.rect.x += (self.direction * self.speed)
        # Check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        # Check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 5
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, grenades_type, direction):
        """Shooting"""
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 3
        self.image = grenades_type
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        """Update Grenade Animation"""
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # Check collision with floor
        if self.rect.bottom + dy > 500:
            dy = 500 - self.rect.bottom
            self.speed = 0

        # Check collision with wall
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1
            dx = self.direction * self.speed

        # update grenade
        self.rect.x += dx
        self.rect.y += dy

        # countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosion)
            # do damage to anyone that is near by
            if abs(self.rect.centerx - player.rect.centerx) < EXPLOSION_RANGE * 2 \
                    and abs(self.rect.centery - player.rect.centery) < EXPLOSION_RANGE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < EXPLOSION_RANGE * 2 \
                        and abs(self.rect.centery - enemy.rect.centery) < EXPLOSION_RANGE * 2:
                    enemy.health -= 50


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        """Shooting"""
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 7):
            img = pygame.image.load(f'img/Variable/Grenade/{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        EXPLOSION_SPEED = 4
        # Update explosion animation
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            # If the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


class Item(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        """Shooting"""
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = items[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        """Check if player pick up box"""
        if pygame.sprite.collide_rect(self, player):
            # Check what kind of item it was
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            if self.item_type == 'Mana':
                player.ammo += 15
            if self.item_type == 'Grenade':
                player.grenades += 5
            # Delete item
            self.kill()


# Create Sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()

# Temp - create items
item = Item('Health', 100, 468)
item_group.add(item)
item = Item('Mana', 300, 468)
item_group.add(item)
item = Item('Grenade', 700, 468)
item_group.add(item)

# Set player position, scale and speed...
player = Character('Player', 100, START_X, START_Y, CHA_SCALE, PLAYER_SPEED, 20, bullet, 10, grenades)
health_bar = Health_bar(85, 9, player.health, player.health)

enemy = Character('Target', 10, 500, 468, CHA_SCALE, ENEMY_SPEED, 20, bullet, 0, grenades)
enemy2 = Character('Skeleton', 10, 800, 468, CHA_SCALE, ENEMY_SPEED, 20, arrow, 0, grenades)
enemy_group.add(enemy)
enemy_group.add(enemy2)
