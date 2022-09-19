"""
This Game was made by:
    64070225    นายวชิรวิทย์ ปรางค์นวรัตน์
    64070237    นายศิวนาถ วรศักดิ์สิริกุล
    64070183    นางสาวปัณณพร จึงเปี่ยมสุข
    64070243    นายสหัสวรรษ บุญเผื่อน

Hello! Welcome to our game codes!
You must be the one who is interesting in coding. (Or you just want to edit the code...)
But anyway, Feel free to explore codes.
But if you don't sure please don't edit the code or the game will be crashed!
Good luck! -Dev
"""

"""
The First part is game config. We recommended not editing anything in here.
"""
start_game = False

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 720

BG = (46, 46, 41)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
FPS = 120

CHA_SCALE = 1
BG_SCALE = 1.4
PLAYER_SPEED = 3
ENEMY_SPEED = 1

GRAVITY = 0.325

SCROLL_THRESH = 200

ROWS = 16
COLS = 50
TILE_SIZES = SCREEN_HEIGHT // ROWS
TILE_TYPES = 70
level = 1
MAX_LEVELS = 6

EXPLOSION_RANGE = 32

ANIMATION_COOL_DOWN = 250
BULLET_COOL_DOWN = 80

"""
The second part is the sprite code where the tile, enemy, player, item, etc. were stored.
You can go and edit some code if you want.
But remember, if the code is wrong, the game also not working.
"""
import pygame
import os
import random
import csv
from pygame.locals import *

screen_scroll = 0
bg_scroll = 0
pygame.display.set_icon(pygame.image.load('icon.png'))
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
        self.vision_2 = pygame.Rect(0, 0, 250, 20)
        self.idling = False
        self.idling_counter = 0

        animation_types = ['Idle', 'Run', 'Jump', 'Death', 'Shoot']
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
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.play_sound = False

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
        screen_scroll = 0
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
            if level != 6:
                jump_fx.play(0)
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Check for collision
        for tile in world.obstacle_list:
            # Check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # if the AI has hit a wall then make it turn around:
                if self.char_type == 'Enemy' or self.char_type == 'Enemy_2':
                    self.direction = -1
                    self.move_counter = 0
            # Check collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # Check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # Check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # Check if collide with player or enemy
        for enemy in enemy_group:
            if enemy.rect.colliderect(player.rect.x + dx, player.rect.y, player.width, player.height) \
                    and enemy.alive is True:
                dx = 0
                if player.vel_y < 0:
                    player.vel_y = 0
                    dy = enemy.rect.bottom - player.rect.top
                elif player.vel_y >= 0:
                    player.vel_y = 0
                    player.in_air = False
                    dy = enemy.rect.top - player.rect.bottom

        # Check if collision with next sign
        next_level = False
        if pygame.sprite.spritecollide(self, next_group, False):
            next_level = True

        # Check if collision with previous sign
        pre_level = False
        if pygame.sprite.spritecollide(self, previous_group, False):
            pre_level = True

        # Check if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT + 50:
            self.health = 0
            dx = 0

        # Check if going off the edges of the screen
        if self.char_type == 'Player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # Update rect position
        self.rect.x += dx
        self.rect.y += dy

        # Update scroll base on player position
        if self.char_type == 'Player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH
                and bg_scroll < (world.level_length * TILE_SIZES) - SCREEN_WIDTH) \
                    or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
        return screen_scroll, next_level, pre_level

    def shoot(self):
        """Shoot"""
        if self.shoot_cool_down == 0 and self.ammo > 0:
            gunfire.play(0)
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
                if not self.in_air and self.vel_y < 1:
                    self.update_action(0)
                    self.idling = True
                    self.idling_counter = 500
            # check if the ai in meat the player
            if self.vision.colliderect(player.rect) and not self.in_air and self.vel_y < 1:
                # stop running and shoot player
                self.update_action(4)
                # shoot
                self.shoot()
            elif self.vision_2.colliderect(player.rect) and not self.in_air and self.vel_y < 1:
                self.flip = True
                self.direction *= -1
                # stop running and shoot player
                self.update_action(4)
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

                    # update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 125 * self.direction, self.rect.centery)
                    self.vision_2.center = (self.rect.centerx - 125 * self.direction, self.rect.centery)
                    # pygame.draw.rect(screen, RED, self.vision)
                    # pygame.draw.rect(screen, GREEN, self.vision_2)

                    if self.move_counter >= TILE_SIZES:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        # Scroll
        self.rect.x += screen_scroll

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
            if self.char_type == 'Player' and not self.play_sound:
                gameover.play(0)
                self.play_sound = True

    # Draw player on the screen!!!
    def draw(self):
        """Yes, Draw Player on the screen"""
        # pygame.draw.rect(screen, RED, self.rect)
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


# Load tile images
# Store tile in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/Tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZES, TILE_SIZES))
    img_list.append(img)

# Load Bullet image
bullet = pygame.image.load('img/Variable/Bullet/Bullet.png').convert_alpha()

# Load Grenade image
grenades = pygame.image.load('img/Variable/Grenade/0.png').convert_alpha()

# Load Item image
health_potion_img = pygame.image.load('img/Variable/Item/Health potion.png').convert_alpha()
mana_potion_img = pygame.image.load('img/Variable/Item/Mana potion.png').convert_alpha()
charge_potion_img = pygame.image.load('img/Variable/Item/Charge potion.png').convert_alpha()

# Load Trap image
trap_image = pygame.image.load('img/Variable/Trap/trap.png').convert_alpha()

items = {
    'Health': health_potion_img,
    'Mana': mana_potion_img,
    'Grenade': charge_potion_img
}


class World():
    def __init__(self):
        """This is my world"""
        self.obstacle_list = []

    def process_data(self, data):
        """Iterate through each value in level data file"""
        self.level_length = len(data[0])
        player = ""
        health_bar = ""
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZES
                    img_rect.y = y * TILE_SIZES
                    tile_data = (img, img_rect)
                    if 0 <= tile <= 11 or 60 <= tile <= 62:
                        self.obstacle_list.append(tile_data)
                    elif 12 <= tile <= 23 or 63 <= tile <= 65:
                        invisible = Invisible(img, x * TILE_SIZES, y * TILE_SIZES)
                        invisible_group.add(invisible)
                    elif 24 <= tile <= 25:
                        water = Water(img, x * TILE_SIZES, y * TILE_SIZES)
                        water_group.add(water)
                    elif tile == 26:
                        item = Item('Grenade', x * TILE_SIZES, y * TILE_SIZES)
                        item_group.add(item)
                    elif tile == 27:
                        item = Item('Health', x * TILE_SIZES, y * TILE_SIZES)
                        item_group.add(item)
                    elif tile == 28:
                        item = Item('Mana', x * TILE_SIZES, y * TILE_SIZES)
                        item_group.add(item)
                    elif tile == 29:
                        player = Character('Player', 100, x * TILE_SIZES, y * TILE_SIZES, CHA_SCALE, PLAYER_SPEED, 20,
                                           bullet, 1, grenades)
                        health_bar = Health_bar(85, 9, player.health, player.health)
                    elif tile == 30:
                        enemy = Character('Enemy', 10, x * TILE_SIZES, y * TILE_SIZES, CHA_SCALE, ENEMY_SPEED, 9999,
                                          bullet, 0, grenades)
                        enemy_group.add(enemy)
                    elif tile == 31:
                        enemy2 = Character('Enemy_2', 10, x * TILE_SIZES, y * TILE_SIZES, CHA_SCALE, ENEMY_SPEED, 9999,
                                           bullet, 0, grenades)
                        enemy_group.add(enemy2)
                    elif tile == 32:
                        campfire = Campfire(x * TILE_SIZES, y * TILE_SIZES)
                        campfire_group.add(campfire)
                    elif 33 <= tile <= 34:
                        sign = Next(img, x * TILE_SIZES, y * TILE_SIZES, 'Next')
                        next_group.add(sign)
                    elif 35 <= tile <= 36:
                        sign = Previous(img, x * TILE_SIZES, y * TILE_SIZES, 'Previous')
                        previous_group.add(sign)
                    elif tile == 37:
                        trap = Trap(img, x * TILE_SIZES, y * TILE_SIZES)
                        trap_group.add(trap)
                    elif tile == 38:
                        trap = Invisible_Trap(img, x * TILE_SIZES, y * TILE_SIZES)
                        invisible_trap_group.add(trap)
                    elif 39 <= tile <= 40 or 68 <= tile <= 69:
                        trap = Falling(img, x * TILE_SIZES, y * TILE_SIZES)
                        falling_group.add(trap)
                    elif 41 <= tile <= 59 or 66 <= tile <= 67:
                        deco = Decoration(img, x * TILE_SIZES, y * TILE_SIZES)
                        decoration_group.add(deco)

        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Health_bar:
    def __init__(self, x, y, health, max_health):
        """Health Bar"""
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # Update with new health
        self.health = health


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, ammo_type, direction):
        """Shooting"""
        pygame.sprite.Sprite.__init__(self)
        self.speed = 5
        self.image = ammo_type
        self.rect = self.image.get_rect()
        self.rect.center = (x, y - 15)
        self.direction = direction
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        """Update Bullet Animation"""
        # Move Bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # Check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        # Check collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        # Check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 20
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 5
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, grenades_type, direction):
        """Also Shooting"""
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 3
        self.image = grenades_type
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        """Update Grenade Animation"""
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # Check for collision with level
        for tile in world.obstacle_list:
            # Check collision with wall
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            # Check collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                # Check if below the ground, i.e. jumping
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # Check if above the ground, i.e. falling
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        # update grenade
        self.rect.x += dx + screen_scroll
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
                player.health -= 99
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < EXPLOSION_RANGE * 2 \
                        and abs(self.rect.centery - enemy.rect.centery) < EXPLOSION_RANGE * 2:
                    enemy.health -= 99


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        """Explosion!!!"""
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
        self.play_sound = False

    def update(self):
        # Scroll
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4
        # Update explosion animation
        if not self.play_sound:
            grenadesound.play(0)
            self.play_sound = True
        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            # If the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


class Trap(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        """Remember, you can't swim in game"""
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZES // 2, y + (TILE_SIZES - self.image.get_height()))

    def update(self):
        """Update"""
        self.rect.x += screen_scroll
        # If character hit the trap
        if pygame.sprite.spritecollide(player, trap_group, False):
            if player.alive:
                player.health -= player.max_health


class Campfire(pygame.sprite.Sprite):
    def __init__(self, x, y):
        """AHHHHH!!! SO HOT!!!"""
        pygame.sprite.Sprite.__init__(self)
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        # Count number of files in folders
        num_of_frames = len(os.listdir('img/Variable/Campfire'))
        for i in range(num_of_frames):
            img = pygame.image.load(f'img/Variable/Campfire/{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * 1),
                                               int(img.get_height()) * 1))
            self.animation_list.append(img)

        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZES // 2, y + (TILE_SIZES - self.image.get_height()))

    def update_animation(self):
        """We will have animation now"""
        # Update image depending on current frame
        self.image = self.animation_list[self.frame_index]
        # Check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOL_DOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list):
            self.frame_index = 0

        # If character hit the fire
        if pygame.sprite.spritecollide(player, campfire_group, False):
            if player.alive:
                player.health -= player.max_health

    def update(self):
        """Update"""
        self.update_animation()
        self.rect.x += screen_scroll


class Falling(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        """Invisible Block for you to jump on"""
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZES // 2, y + (TILE_SIZES - self.image.get_height()))
        self.falling = False
        self.play_sound = False

    def update(self):
        """Update"""
        self.rect.x += screen_scroll
        # Check if player near the stick
        if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZES and self.rect.y <= player.rect.y \
                or self.falling:
            if not self.play_sound:
                fallingleaf.play(0)
                self.play_sound = True
            self.rect.y += 5
            self.falling = True
        # Check if falling off screen
        if self.rect.top <= -SCREEN_HEIGHT:
            self.kill()
        # Check collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        # Check collision with characters
        if pygame.sprite.spritecollide(player, falling_group, False):
            if player.alive:
                player.health -= player.max_health
                self.kill()


class Invisible(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        """Invisible Block for you to jump on"""
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZES // 2, y + (TILE_SIZES - self.image.get_height()))

    def update(self):
        """Update"""
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        """Remember, you can't swim in game"""
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZES // 2, y + (TILE_SIZES - self.image.get_height()))

    def update(self):
        """Update"""
        self.rect.x += screen_scroll


class Next(pygame.sprite.Sprite):
    def __init__(self, img, x, y, type):
        """Go to the next or previous level"""
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZES // 2, y + (TILE_SIZES - self.image.get_height()))
        self.type = type

    def update(self):
        """Update"""
        self.rect.x += screen_scroll


class Previous(pygame.sprite.Sprite):
    def __init__(self, img, x, y, type):
        """Go to the next or previous level"""
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZES // 2, y + (TILE_SIZES - self.image.get_height()))
        self.type = type

    def update(self):
        """Update"""
        self.rect.x += screen_scroll


class Invisible_Trap(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        """If you can't see, it doesn't mean that it's not there."""
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZES // 2, y + (TILE_SIZES - self.image.get_height()))

    def update(self):
        """Update"""
        self.rect.x += screen_scroll
        # If character hit the fire
        if pygame.sprite.spritecollide(player, invisible_trap_group, False):
            self.image = pygame.transform.scale(trap_image, (TILE_SIZES, TILE_SIZES))
            if player.alive:
                    player.health -= player.max_health


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        """Wow, beautiful!"""
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZES // 2, y + (TILE_SIZES - self.image.get_height()))

    def update(self):
        """Update"""
        self.rect.x += screen_scroll


class Item(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        """Item"""
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = items[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZES // 2, y + (TILE_SIZES - self.image.get_height()))

    def update(self):
        """Check if player pick up box"""
        # Scroll
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self, player):
            # Check what kind of item it was
            if self.item_type == 'Health':
                collect.play()
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            if self.item_type == 'Mana':
                collect.play()
                player.ammo += 10
            if self.item_type == 'Grenade':
                collect.play()
                player.grenades += 2
            # Delete item
            self.kill()

# Button class
class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False

        # get mouse position
        pos = pygame.mouse.get_pos()

        # check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


# Create Button
# Button images
start_image = pygame.image.load('img/Variable/Button/start_button.png').convert_alpha()
exit_image = pygame.image.load('img/Variable/Button/exit_button.png').convert_alpha()
restart_image = pygame.image.load('img/Variable/Button/restart_button.png').convert_alpha()

start_button = Button(SCREEN_WIDTH // 2 - 190, SCREEN_HEIGHT // 2 - 70, start_image, 2)
exit_button = Button(SCREEN_WIDTH // 2 - 190, SCREEN_HEIGHT // 2 + 120, exit_image, 2)
restart_button = Button(SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 20, restart_image, 2)

# Create Sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
invisible_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
campfire_group = pygame.sprite.Group()
trap_group = pygame.sprite.Group()
next_group = pygame.sprite.Group()
previous_group = pygame.sprite.Group()
falling_group = pygame.sprite.Group()
invisible_trap_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()


# Create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
# Load in level data and create world
with open(f'level/level{level}.csv', newline='') as csv_file:
    reader = csv.reader(csv_file, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

"""
This is the final path where all the second path will draw on and start to running the game!
(If you want to edit something, go to the second path)
"""
# Screen settings and display
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('TTMP-PROJECT')

# Set Frame rate
clock = pygame.time.Clock()

# Defined player action variables
move_left = False
move_right = False
shoot = False
grenade = False
grenade_thrown = False

font = pygame.font.SysFont('Futura', 30)

# Load images
wallpaper = pygame.image.load('img/Background/Wallpaper.png')

background_image = pygame.image.load('img/Background/Forest.png').convert_alpha()
background_image = pygame.transform.scale(background_image, (int(background_image.get_width() ),
                                               int(background_image.get_height()) ))
game_over_image = pygame.image.load('img/Variable/Text/Game Over.png').convert_alpha()
game_over_image = pygame.transform.scale(game_over_image, (int(game_over_image.get_width() * 2.5),
                                               int(game_over_image.get_height() * 2.5)))
wasd_image = pygame.image.load('img/Variable/Text/WASD.png').convert_alpha()
wasd_image = pygame.transform.scale(wasd_image, (int(wasd_image.get_width() * 2.5),
                                               int(wasd_image.get_height() * 2.5)))
end_image = pygame.image.load('img/Variable/Text/The end.png').convert_alpha()
end_image = pygame.transform.scale(end_image, (int(SCREEN_WIDTH),
                                               int(SCREEN_HEIGHT)))

# Load sound
fallingleaf = pygame.mixer.Sound('music/Fallingleaf.wav')
fallingleaf.set_volume(0.3)
gunfire = pygame.mixer.Sound('music/Gunfire.wav')
gunfire.set_volume(0.05)
gameover = pygame.mixer.Sound('music/Gameover.wav')
gameover.set_volume(0.05)
run_fx = pygame.mixer.Sound('music/Running.wav')
run_fx.set_volume(0.1)
jump_fx = pygame.mixer.Sound('music/Jump.wav')
jump_fx.set_volume(0.1)
collect = pygame.mixer.Sound('music/Collect.wav')
collect.set_volume(0.1)
grenadesound = pygame.mixer.Sound('music/Grenade.wav')
grenadesound.set_volume(0.05)
the_end = pygame.mixer.Sound('music/The End.wav')
the_end.set_volume(0.1)


def draw_text(text, font, text_col, x, y):
    """Draw Text"""
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    """Screen BG Woo!!!"""
    screen.fill(BG)
    width = background_image.get_width()

    for x in range(5):
        screen.blit(background_image, ((x * width) - bg_scroll, 0))

    if level == 1:
        screen.blit(wasd_image, (250 - bg_scroll, 80))


def reset_level():
    """Reset everything"""
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    item_group.empty()
    explosion_group.empty()
    invisible_group.empty()
    water_group.empty()
    campfire_group.empty()
    next_group.empty()
    previous_group.empty()
    trap_group.empty()
    falling_group.empty()
    invisible_trap_group.empty()
    decoration_group.empty()

    # Create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    return data


# Run the game YAY!!!
run = True

pygame.mixer.music.load('music/Soundtrack.wav')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)

the_end_play = False
while run:
    
    clock.tick(FPS)
    
    if not start_game:
        # Draw main menu
        screen.blit(wallpaper, (0,0))
        # Add buttons
        if start_button.draw(screen):
            start_game = True
        if exit_button.draw(screen):
            run = False
    else:
        # Draw Background
        draw_bg()
        # Draw Tile map
        world.draw()
        # show health bar
        draw_text(f'Health: {player.health} / {player.max_health}', font, BLACK, 10, 30)
        # health_bar.draw(player.health)

        # show ammo
        draw_text(f'Ammo: {player.ammo}', font, BLACK, 10, 60)

        # show grenade
        draw_text(f'Grenade: {player.grenades}', font, BLACK, 10, 90)

        campfire_group.update()
        campfire_group.draw(screen)

        # Update and draw group
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_group.update()
        invisible_group.update()
        water_group.update()
        next_group.update()
        previous_group.update()
        trap_group.update()
        falling_group.update()
        invisible_trap_group.update()
        decoration_group.update()
        player.update()

        item_group.draw(screen)
        next_group.draw(screen)
        previous_group.draw(screen)
        trap_group.draw(screen)
        falling_group.draw(screen)
        invisible_trap_group.draw(screen)
        decoration_group.draw(screen)
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        water_group.draw(screen)
        invisible_group.draw(screen)

        if player.alive:
            # Update player actions
            if shoot:
                player.update_action(4) # Shoot
                player.shoot()
            elif grenade and not grenade_thrown and player.grenades > 0:
                grenade = Grenade(
                    player.rect.centerx + (0.7 * player.rect.size[0] * player.direction),
                    player.rect.top, grenades,
                    player.direction)
                grenade_group.add(grenade)
                player.grenades -= 1
                grenade_thrown = True
            elif player.in_air:
                player.update_action(2)  # 2 : Jump
            elif move_left or move_right:
                player.update_action(1)  # 1 : Run
            else:
                player.update_action(0)  # 0 : Idle
            screen_scroll, next_level, pre_level = player.move(move_left, move_right)
            bg_scroll -= screen_scroll

            # Check if player go to next or previous level
            if next_level:
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    # Load level in data and create world
                    with open(f'level/level{level}.csv', newline='') as csv_file:
                        reader = csv.reader(csv_file, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

            elif level == 6:
                screen.blit(end_image, (0, 0))
                pygame.mixer.music.fadeout(1000)
                player.grenades = 0
                player.ammo = 0
                if not the_end_play:
                    the_end.play(0)
                    the_end_play = True

            elif pre_level:
                level -= 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    # Load level in data and create world
                    with open(f'level/level{level}.csv', newline='') as csv_file:
                        reader = csv.reader(csv_file, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

        else:
            screen_scroll = 0
            level = 1
            screen.blit(game_over_image, (200, 125))
            if restart_button.draw(screen):
                bg_scroll = 0
                world_data = reset_level()
                # Load level in data and create world
                with open(f'level/level{level}.csv', newline='') as csv_file:
                    reader = csv.reader(csv_file, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player, health_bar = world.process_data(world_data)

    for event in pygame.event.get():
        # Quit Game Event
        if event.type == pygame.QUIT:
            run = False
            pygame.mixer.music.fadeout(1000)
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

        # Running Sound
            if move_left or move_right:
                if level != 6:
                    run_fx.play(0)


    pygame.display.update()

pygame.quit()

"""Thanks for watching!"""
