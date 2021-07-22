import arcade
import math
import os

PATH = os.path.dirname(os.path.abspath(__file__))


class Projectile(arcade.Sprite):
    """ make the projectile """

    def __init__(self, file, scale=1, angle=0, damage=1, speed=10, max_range=400, min_range=10, does_stick=False):
        super().__init__(file, scale)
        self.damage = damage
        self.speed = speed
        self.does_stick = does_stick
        self.orientation_adjustment = angle
        self.max_range = max_range
        self.min_range = min_range
        self.start_pos = None
        self.power = 0

    def shoot(self, player_sprite, dest_x, dest_y):

        projectile_x = player_sprite.view_position[0]
        projectile_y = player_sprite.view_position[1]
        self.position = player_sprite.position
        self.start_pos = player_sprite.position

        x_diff = dest_x - projectile_x
        y_diff = dest_y - projectile_y
        angle = math.atan2(y_diff, x_diff)

        size = max(player_sprite.width, player_sprite.height)

        self.center_x += size * math.cos(angle)
        self.center_y += size * math.sin(angle)

        self.change_x = math.cos(angle) * self.speed
        self.change_y = math.sin(angle) * self.speed

        self.angle = math.degrees(angle) - self.orientation_adjustment

        return self


class Shot(Projectile):
    """ Shot preset """

    def __init__(self, damage=1, speed=1, position=None):
        super().__init__(PATH+"/resources/projectile.png", .2,
                         90, damage, speed, does_stick=True)
        self.orientation_adjustment = 90
        if position != None:
            self.position = position
