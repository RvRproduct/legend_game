import arcade
import random
import os
import main

CHARACTER_SCALING = 1

# How fast to move, and how fast to run the animation
MOVEMENT_SPEED = 5
UPDATES_PER_FRAME = 5

# Constants for the direction for the player
RIGHT_FACING = 0
LEFT_FACING = 1

PATH = os.path.dirname(os.path.abspath(__file__))


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class Player(arcade.Sprite):
    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between images
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Jumping?
        self.jumping = False

        # hp and ect
        self.hp = 10
        self.view_position = self.position
        self.speed = 5

        # Load Textures
        self.player_texture_pair = load_texture_pair(
            PATH+"/resources/player.png")

        self.texture = self.player_texture_pair[0]

        # Adjust the collision box. Default includes too much empty space
        # side-to-side. Box is centered at sprite center, (0, 0)
        #self.points = [[-22, -22], [22, -22], [22, 22], [-22, 22]]
        # self.set_hit_box(self.player_texture_pair)
        self.points = [[-16, -16], [16, -16], [16, 16], [-16, 16]]

    def update_animation(self, delta_time: float = 1/60):
        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Idle animation
        if self.change_x == 0:
            self.texture = self.player_texture_pair[self.character_face_direction]
            return

    #     # Figure out if we need to change direction
    #     if self.change_x < 0 and self.character_face_direction != LEFT_FACING:
    #         self.character_face_direction = LEFT_FACING
    #     elif self.change_x > 0 and self.character_face_direction != RIGHT_FACING:
    #         self.character_face_direction = RIGHT_FACING

    #     # Idle animation
    #     # print(self.textures[0][0])
    #     if self.change_x == 0 and self.change_y == 0:
    #         self.texture = self.textures[0][0]
    #         return

    #     # Player movement animation
    #     self.cur_texture += 1
    #     if self.cur_texture > 8 * UPDATES_PER_FRAME:
    #         self.cur_texture = 0
    #     frame = self.cur_texture // UPDATES_PER_FRAME
    #     direction = self.character_face_direction
    #     self.texture = self.textures[direction][frame]
