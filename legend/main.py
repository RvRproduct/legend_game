import arcade
from arcade.sprite_list import check_for_collision_with_list
import player
import enemy
import projectile
import os
import math

SCREEN_WIDTH = 815
SCREEN_HEIGHT = 700
SCREEN_TITLE = "LEGEND"

CHARACTER_SCALING = 1
TILE_SCALING = 1
GOAL_SCALING = 1
SPRITE_PIXEL_SIZE = 32
GRID_PIXEL_SIZE = (TILE_SCALING * SPRITE_PIXEL_SIZE)
GRAVITY = 1

# movement speed and animation speed
MOVEMENT_SPEED = 5
PLAYER_JUMP_SPEED = 15
UPDATES_PER_FRAME = 5
SHOT_SPEED = 5

# Player direction
RIGHT_FACING = 0
LEFT_FACING = 1

PLAYER_START_X = SPRITE_PIXEL_SIZE * TILE_SCALING * 2
PLAYER_START_Y = SPRITE_PIXEL_SIZE * TILE_SCALING * 1

# viewpoint
LEFT_VIEWPORT_MARGIN = 75
RIGHT_VIEWPORT_MARGIN = 75
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 150

# music volume
MUSIC_VOLUME = 0.5

# path
PATH = os.path.dirname(os.path.abspath(__file__))


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        """ Set up the game and initialize the variables. """
        super().__init__(width, height, title)

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        # lists
        self.goals_list = None
        self.wall_list = None
        self.enemies_list = None
        self.breakable_walls_list = None
        self.goals_blockade_list = None
        self.shoot_list = None
        self.background_list = None
        self.player_list = None
        self.player = None
        self.enemy = None

        self.physics_engine = None

        # map change
        self.map_change = 1

        # Used to track scrolling
        self.view_bottom = 0
        self.view_left = 0

        self.goal = False

        # sound effects?

    def setup(self, map_change):

        # track scrolling
        self.view_bottom = 0
        self.view_left = 0

        # lists
        self.player_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.goals_list = arcade.SpriteList(use_spatial_hash=True)
        self.shoot_list = arcade.SpriteList()

        # Set up the player
        self.player = player.Player()

        self.player.center_x = PLAYER_START_X
        self.player.center_y = PLAYER_START_Y

        self.player_list.append(self.player)

        # Set the background color
        arcade.set_background_color(arcade.color.WHITE_SMOKE)

        # Layers setup
        walls_layer_name = "Walls"
        goals_layer_name = "Goals"
        enemies_layer_name = "Enemies"
        breakable_walls_layer_name = "BreakableWalls"
        goals_blockade_layer_name = "BlockadeGoals"
        background_layer_name = "Background"

        # name of the map that will load
        map_name = PATH + f"/resources/maps/map_{self.map_change}.tmx"

        # reading the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # background
        self.background_list = arcade.tilemap.process_layer(my_map,
                                                            background_layer_name, TILE_SCALING)

        # walls
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=walls_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        # Lists setup
        self.goals_list = arcade.tilemap.process_layer(
            my_map, goals_layer_name, TILE_SCALING)
        self.enemies_list = arcade.tilemap.process_layer(
            my_map, enemies_layer_name, TILE_SCALING)
        self.goals_blockade_list = arcade.tilemap.process_layer(
            my_map, goals_blockade_layer_name, TILE_SCALING)
        self.breakable_walls_list = arcade.tilemap.process_layer(
            my_map, breakable_walls_layer_name, TILE_SCALING)

        # adding breakable and blockade to the wall list
        for x in self.breakable_walls_list:
            self.wall_list.append(x)

        for x in self.goals_blockade_list:
            self.wall_list.append(x)

        # Set background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # physics engine for platformer
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, self.wall_list, gravity_constant=GRAVITY)

        spawns = enemy.get_enemy_spawns(self.map_change)
        if spawns != None:
            for each in spawns:
                self.enemies_list.append(enemy.Enemy(spawns[0], spawns[1]))

        self.music_count = 0

    def on_draw(self):
        """
        Render the screen
        """
        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw the sprites
        self.wall_list.draw()
        self.background_list.draw()
        self.wall_list.draw()
        self.breakable_walls_list.draw()
        self.goals_list.draw()
        self.goals_blockade_list.draw()
        self.enemies_list.draw()
        self.shoot_list.draw()
        self.player_list.draw()

        # info on screen
        amount_of_enemies_text = f"Enemies: {len(self.enemies_list)}"
        if len(self.enemies_list) == 0:
            enemy_amount_color = arcade.csscolor.BLUE
        else:
            enemy_amount_color = arcade.csscolor.RED

        health_text = f"Health: {self.player.hp}"
        if self.player.hp <= 3:
            health_color = arcade.csscolor.RED
        else:
            health_color = arcade.csscolor.BLUE

        # Draw info on the screen
        arcade.draw_text(amount_of_enemies_text, 10 + self.view_left,
                         10 + self.view_bottom, enemy_amount_color, 20)
        arcade.draw_text(health_text, 10 + self.view_left, 30 + self.view_bottom,
                         health_color, 20)

    def process_keychange(self):
        """ Jumping and change in keys """
        if self.up_pressed:
            if self.physics_engine.can_jump(y_distance=10) and not self.jump_needs_reset:
                self.player.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                arcade.play_sound("jump")

        # Process left/right
        if self.right_pressed and not self.left_pressed:
            self.player.change_x = MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player.change_x = -MOVEMENT_SPEED
        else:
            self.player.change_x = 0

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed
        """
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        """
        Called when the user releases a key.
        """
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def on_mouse_release(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            shot = arcade.Sprite(
                PATH+"/resources/projectile.png", TILE_SCALING)
            # shot = projectile.Shot()
            # self.shoot_list.append(shot)
            start_x = self.player.center_x
            start_y = self.player.center_y
            shot.center_x = start_x
            shot.center_y = start_y

            # scrolling purposes
            dest_x = x
            dest_y = y

            # math things for angles
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)

            # correcting the angle so it doesnt look sideways
            shot.angle = math.degrees(angle)

            # speed change
            shot.change_x = math.cos(angle) * SHOT_SPEED
            shot.change_y = math.sin(angle) * SHOT_SPEED

            # add the projectile to the list
            self.shoot_list.append(shot)

    # def on_mouse_release(self, x, y, button, modifiers):
    #     if button == arcade.MOUSE_BUTTON_LEFT:
    #         for item in self.shoot_list:
    #             item.kill()
            # shot = self.shoot_list.pop()
            # shot.min_range = max(
            #     int(shot.max_range, shot.min_range))
            # self.shoot_list.append(shot.shoot(
            #     self.player, self._mouse_x, self._mouse_y))

    def on_update(self, delta_time):
        """ Movemoent and game logic """

        # Move the player with the physics engine
        self.physics_engine.update()

        # jump
        if self.physics_engine.can_jump():
            self.player.can_jump = False
        else:
            self.player.can_jump = True

        # Move the player
        self.player.update_animation(delta_time)

        # Update the players animation
        # self.player_list.update_animation()

        # for view port
        changed = False

        # if the player dies
        if self.player.hp <= 0:
            self.setup(self.map_change)
            arcade.play_sound("death sound")

        # for combat

        self.shoot_list.update()

        for shot in self.shoot_list:
            hit_enemy = arcade.check_for_collision_with_list(
                shot, self.enemies_list)
            hit_wall_break = arcade.check_for_collision_with_list(
                shot, self.breakable_walls_list)
            hit_wall = arcade.check_for_collision_with_list(
                shot, self.wall_list)

            if len(hit_enemy) > 0:
                shot.remove_from_sprite_lists()
                for x in self.enemies_list:
                    x.kill()
            if len(hit_wall_break) > 0:
                shot.remove_from_sprite_lists()
                for x in self.breakable_walls_list:
                    x.remove_from_sprite_lists()
            if len(hit_wall) > 0:
                shot.remove_from_sprite_lists()

            if shot.bottom > self.width or shot.top < 0 or shot.right < 0 or shot.left > self.width:
                shot.remove_from_sprite_lists()

        for enemy in self.enemies_list:
            enemy.chase(self.player.center_x, self.player.center_y)
            if arcade.check_for_collision(enemy, self.player):
                self.player.hp -= enemy.damage
                self.player.center_x += (self.player.center_x -
                                         enemy.center_x)
                self.player.center_y += (self.player.center_y -
                                         enemy.center_y)
                bump_list = arcade.check_for_collision_with_list(
                    enemy, self.wall_list)
                if len(bump_list) > 0:
                    enemy.center_x += (enemy.center_x-bump_list[0].center_x)
                    enemy.center_y += (enemy.center_y-bump_list[0].center_y)

                # arcade.play_sound("break sou
        for y in self.breakable_walls_list:
            breakable_walls_hit_list = arcade.check_for_collision_with_list(y,
                                                                            self.shoot_list)
            if len(breakable_walls_hit_list):
                # arcade.play_sound(self.wall_break_sound)
                y.kill()

        if (len(self.enemies_list) <= 0):
            for x in self.goals_blockade_list:
                x.kill()

            # for combat
            # for item in self.shoot_list:
            #     if (len(item.collides_with_list(self.wall_list)) > 0) or (arcade.get_distance(item.position[0], item.position[1], item.start_pos[0], item.start_pos[1]) > item.min_range):
            #         if item.does_stick:
            #             item.change_x = 0
            #             item.change_y = 0
            #             item.kill()
            #         else:
            #             item.kill()
            #     shot_list = arcade.check_for_collision_with_list(
            #         item, self.enemies_list)
            #     for self.person in shot_list:
            #         # arcade.play_sound(self.damage_taken_player_sound)
            #         self.person.hp -= item.damage
            #         item.kill()

            # self.shoot_list.update()
            # for enemy in self.enemies_list:
            #     hit_list = arcade.check_for_collision_with_list(
            #         enemy, self.shoot_list)
            #     for action in hit_list:
            #         arcade.play_sound("hit enemy")
            #         enemy.hp -= action.damage
            #         action.damage = 0
            #     if enemy.hp <= 0:
            #         arcade.play_sound("enemy die")
            #         enemy.kill()

            # opening area to enter the goal

        # This takes care of scrolling and tracking for the viewport

         # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player.left < left_boundary:
            self.view_left -= left_boundary - self.player.left
            changed = True

        # Scroll right
        right_boundary = self.view_left + 250 - RIGHT_VIEWPORT_MARGIN
        if self.player.right > right_boundary:
            self.view_left += self.player.right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.view_bottom + 250 - TOP_VIEWPORT_MARGIN
        if self.player.top > top_boundary:
            self.view_bottom += self.player.top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player.bottom
            changed = True

        if changed:
            # Scrolls by ints
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left, 300 + self.view_left,
                                self.view_bottom,
                                300 + self.view_bottom)

        # if we reach the goal
        goals_hit_list = arcade.check_for_collision_with_list(
            self.player, self.goals_list)

        if len(goals_hit_list) > 0:
            self.map_change += 1
            self.setup(self.map_change)
            self.view_left = 0
            self.view_bottom = 0
            changed = True

        # Aiming
        self.player.view_position = [
            (self.player.center_x - self.view_left), (self.player.center_y-self.view_bottom)]


def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup(window.map_change)
    arcade.run()


if __name__ == "__main__":
    main()
