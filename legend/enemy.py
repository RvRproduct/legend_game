import arcade
import os
import projectile
import math


ENEMY_SCALING = 1

# How fast to move, and how fast to run the animation
MOVEMENT_SPEED = 5
UPDATES_PER_FRAME = 5

# Constants for the direction for the player
RIGHT_FACING = 0
LEFT_FACING = 1

PLAYER_START_X = 0
PLAYER_START_Y = 0

PATH = os.path.dirname(os.path.abspath(__file__))
# , x, y, image=PATH+"", size=.3


def get_enemy_spawns(index):
    """ Get enemy spawns """
    enemy_spawns = [None, (250, 300), (500, 400), (100, 150), None, None]
    print(enemy_spawns[index])

    return enemy_spawns[index]


class Enemy(arcade.Sprite):
    def __init__(self, x, y, image=PATH+'/resources/enemy.png', size=1):
        """ Initializer for the enemy. """

        super().__init__(image, size)

        # Default to face-right
        self.enemy_face_direction = RIGHT_FACING

        self.damage = 1

        self.center_x = x
        self.center_y = y

        self.speed = 1.25
        self.view_position = self.position
        self.path = None
        self.count = 3

    def chase(self, dest_x, dest_y):
        """
        This function will move the current sprite towards the player
        """
        if self.center_y < dest_y:
            self.center_y += min(self.speed, dest_y - self.center_y)
        elif self.center_y > dest_y:
            self.center_y -= min(self.speed, self.center_y - dest_y)

        if self.center_x < dest_x:
            self.center_x += min(self.speed, dest_x - self.center_x)
        elif self.center_x > dest_x:
            self.center_x -= min(self.speed, self.center_x - dest_x)
