#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2019 Joakim Winum Lien
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Py Snake CLI Game

This is an implementation of the classic snake game.

This game has been ported from the PHP version of the game:
https://github.com/joakimwinum/php-snake

Author: Joakim Winum Lien <joakim@winum.xyz>
License: https://opensource.org/licenses/mit-license.html MIT License
Version: 1.0.0
Repository: https://github.com/joakimwinum/py-snake
"""

import os
import copy
import random
import select
import subprocess
import sys
import time


# functions

# create functions

def create_player():
    player_sprite = '&'
    return [[40, 12, player_sprite], [39, 12, player_sprite], [38, 12, player_sprite]]


def create_frame_wall():
    frame_wall_array = []

    wall_sprite = '#'

    i = 0
    while i < board_x:
        j = 0
        while j < board_y:
            if i == 0 or i == board_x - 1 or j == 0 or j == board_y - 1:
                # create the frame wall
                frame_wall_array.append([i, j, wall_sprite])
            j += 1
        i += 1

    return frame_wall_array


def create_background():
    background_array = []

    background_sprite = ' '

    i = 0
    while i < board_x:
        j = 0
        while j < board_y:
            # create the background
            background_array.append([i, j, background_sprite])
            j += 1
        i += 1

    return background_array


def draw(entities):
    global blank_board
    global cache_draw

    board = ''

    # create a blank board array if it is not already done
    if '0,0' not in blank_board:
        j = 0
        while j < board_y:
            i = 0
            while i < board_x:
                blank_board[''+str(i)+','+str(j)+''] = '%'
                i += 1
            j += 1
    board_array = copy.copy(blank_board)

    # draw all the entities onto the board array
    for entity in entities:
        entity_is_multidimensional = True
        try:
            entity[0][0]
        except (NameError, KeyError, TypeError):
            entity_is_multidimensional = False
        if entity_is_multidimensional:
            for coo in entity:
                board_array[''+str(coo[0])+','+str(coo[1])+''] = coo[2]
        else:
            board_array[''+str(entity[0])+','+str(entity[1])+''] = entity[2]

    # store the current entities in the draw cache
    if cache_draw:
        blank_board = board_array
        cache_draw = False

    # convert the board array to string
    j = 0
    while j < board_y:
        i = 0
        while i < board_x:
            # add margin on the left side of the board
            if i == 0:
                board += left_margin

            # draw the board array
            board += board_array[''+str(i)+','+str(j)+'']

            # add a line break on end of each line
            if i == board_x - 1:
                board += '\n'
            i += 1
        j += 1

    board = board.rstrip()

    # return the board string
    return board


# other functions

def player_function(player):
    global snake_len

    snake_len = len(player)
    head_direction = None
    north = 'north'
    south = 'south'
    west = 'west'
    east = 'east'

    # determine the direction of the players head
    if player[0][0] > player[1][0]:
        head_direction = east
    elif player[0][0] < player[1][0]:
        head_direction = west
    elif player[0][1] < player[1][1]:
        head_direction = north
    elif player[0][1] > player[1][1]:
        head_direction = south

    # move player with or without input
    if key is not None:
        if key == 'w' and (head_direction == west or head_direction == east):
            player = move_player(player, north)
        elif key == 'a' and (head_direction == north or head_direction == south):
            player = move_player(player, west)
        elif key == 's' and (head_direction == west or head_direction == east):
            player = move_player(player, south)
        elif key == 'd' and (head_direction == north or head_direction == south):
            player = move_player(player, east)
    else:
        player = move_player(player, head_direction)

    return player


def move_player(player, direction):
    north = 'north'
    south = 'south'
    west = 'west'
    east = 'east'

    # take off the tail
    if not increase_player():
        player.pop()

    # create the new head
    new_head = copy.copy(player[0])

    # move the new head
    if direction == north:
        new_head[1] -= 1
        engine.fps = engine.fps_vertical
    elif direction == west:
        new_head[0] -= 1
        engine.fps = engine.fps_horizontal
    elif direction == south:
        new_head[1] += 1
        engine.fps = engine.fps_vertical
    elif direction == east:
        new_head[0] += 1
        engine.fps = engine.fps_horizontal

    # add the new head on
    player = [new_head] + player

    return player


def increase_player(set_variable=False, int_variable=None):
    global snake_old_len
    global do_increase_player
    global increase_interval
    global score

    score = snake_len - 3

    if int_variable is not None:
        increase_interval = int_variable

    if set_variable:
        snake_old_len = snake_len

    if snake_len >= snake_old_len + increase_interval:
        do_increase_player = False
    else:
        do_increase_player = True

    return do_increase_player


def collision_testing(player, point_dot):
    global update_point_dot

    # players head
    player_head = player[0]

    # check for collision with wall
    for wall in frame_wall:
        if wall[0] == player_head[0] and wall[1] == player_head[1]:
            game_over()

    # player eats point dot
    if player_head[0] == point_dot[0] and player_head[1] == point_dot[1]:
        increase_player(True)
        update_point_dot = True

    # check if player head touches its own tail
    for key, part in enumerate(player, start=0):
        if key == 0:
            # skip head
            continue

        if player_head[0] == part[0] and player_head[1] == part[1]:
            game_over()


def game_over():
    screen = left_margin
    screen += global_game_title
    screen += ' Game Over '
    pad_score = str(score).rjust(4, '0')
    right_pointing_triangle_sprite = '>'
    screen += right_pointing_triangle_sprite
    screen += ' Score: '+pad_score
    if dev_mode:
        screen += ' [DevMode]'

    screen += '\n'
    screen += board

    # clear the screen
    engine.clear_screen()

    # print the screen
    print(screen)

    engine.reset_tty()

    exit()


def generate_new_coordinates(point_dot, player):
    while True:
        # get random coordinates
        rand_x = random.randint(1, (board_x-2))
        rand_y = random.randint(1, (board_y-2))

        # check if the player already is on the new coordinates
        do_continue = False
        for part in player:
            if part[0] == rand_x and part[1] == rand_y:
                do_continue = True
                break
        if do_continue:
            continue

        # check if the new coordinates are in the old place of the point dot
        if point_dot is not None and point_dot[0] == rand_x and point_dot[1] == rand_y:
            continue

        break

    return [rand_x, rand_y]


def point_dot_function(player, point_dot=None):
    global update_point_dot

    point_dot_sprite = '*'

    # generate the first dot
    if point_dot is None:
        coordinates = generate_new_coordinates(None, player)
        point_dot = [coordinates[0], coordinates[1], point_dot_sprite]

    # update the dot
    if update_point_dot:
        coordinates = generate_new_coordinates(point_dot, player)
        point_dot = [coordinates[0], coordinates[1], point_dot_sprite]
        update_point_dot = False

    return point_dot


def print_stats():
    # add left margin
    string = left_margin

    # display game name
    string += global_game_title

    # display score
    pad_score = str(score).rjust(4, '0')
    string += ' points: '+pad_score

    # display extra stats in dev mode
    if dev_mode:
        # display snake length
        pad_snake_len = str(snake_len).rjust(4, '0')
        string += ', length: '+pad_snake_len

        # display total number of frames
        pad_frames = str(total_number_of_frames).rjust(4, '0')
        string += ', total frames: '+pad_frames

        # display frames per second
        pad_fps = str(engine.fps).rjust(4, '0')
        string += ', FPS: '+pad_fps

    # add new line
    string += '\n'

    return string


def key_actions():
    global dev_mode
    global update_point_dot

    # do actions upon certain key presses
    if key is not None:
        if key == 'q':
            # exit the game
            engine.reset_tty()
            exit()
        elif key == 'i':
            # increase length
            if dev_mode:
                increase_player(True, 40)
        elif key == 'u':
            # increase length
            if dev_mode:
                increase_player(True, 140)
        elif key == 'r':
            # reset length increase
            if dev_mode:
                increase_player(False, 1)
        elif key == 'e':
            # increase fps
            if dev_mode:
                engine.fps_horizontal = 25
                engine.fps_vertical = int(engine.fps_horizontal*engine.fps_factor)
        elif key == 'y':
            # increase fps by 1 fps
            if dev_mode:
                engine.fps_horizontal = engine.fps_horizontal + 1
                engine.fps_vertical = int(engine.fps_horizontal*engine.fps_factor)
        elif key == 'n':
            # replace point dot
            if dev_mode:
                update_point_dot = True
        elif key == 't':
            # activate dev mode
            if not dev_mode:
                dev_mode = True


class PyGameEngine:
    """Class PyGameEngine

    The game engine takes care of mainly three things:
    * clearing the screen
    * syncing the game loop
    * detecting key presses

    Remember to call the TTY reset method before exit if the built in key
    detection function have been used.

    Author: Joakim Winum Lien <joakim@winum.xyz>
    License: https://opensource.org/licenses/mit-license.html MIT License
    Version: 1.0.0
    """

    def __init__(self):
        self._game_time_beginning = None
        self._game_time_end = None
        self._fps = None
        self._fps_horizontal = None
        self._fps_vertical = None
        self._fps_factor = None
        self._os_variable = None
        self._key_read_timeout = None
        self._tty_settings = None

    @property
    def game_time_beginning(self):
        return self._game_time_beginning

    @game_time_beginning.setter
    def game_time_beginning(self, value):
        self._game_time_beginning = value

    @property
    def game_time_end(self):
        return self._game_time_end

    @game_time_end.setter
    def game_time_end(self, value):
        self._game_time_end = value

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, value):
        self._fps = value

    @property
    def fps_horizontal(self):
        return self._fps_horizontal

    @fps_horizontal.setter
    def fps_horizontal(self, value):
        self._fps_horizontal = value

    @property
    def fps_vertical(self):
        return self._fps_vertical

    @fps_vertical.setter
    def fps_vertical(self, value):
        self._fps_vertical = value

    @property
    def fps_factor(self):
        return self._fps_factor

    @fps_factor.setter
    def fps_factor(self, value):
        self._fps_factor = value

    @property
    def os_variable(self):
        return self._os_variable

    @os_variable.setter
    def os_variable(self, value):
        self._os_variable = value

    @property
    def key_read_timeout(self):
        return self._key_read_timeout

    @key_read_timeout.setter
    def key_read_timeout(self, value):
        self._key_read_timeout = value

    @property
    def tty_settings(self):
        return self._tty_settings

    @tty_settings.setter
    def tty_settings(self, value):
        self._tty_settings = value

    @staticmethod
    def microtime_now():
        microtime = time.time()

        time_variable = str(microtime).split('.')
        timestamp = int(time_variable[0])
        microseconds = int(int(time_variable[1])/100)

        return [microseconds, timestamp]

    def fps_sync(self):
        """This method sets a sleep depending on chosen fps

        Put this at the end of a game loop to sync with the fps you have chosen.
        """
        # get the time from the bottom of the code
        self.game_time_end = self.microtime_now()

        if self.game_time_beginning is not None:
            time_beginning = self.game_time_beginning[0]
        else:
            time_beginning = None
        time_end = self.game_time_end[0]

        if time_beginning is None:
            self.key_read_timeout = 100
            self.game_time_beginning = self.microtime_now()
            return False

        # the loop is taking longer than 1 second
        if self.game_time_end[1] - self.game_time_beginning[1] > 1:
            self.key_read_timeout = 100
            self.game_time_beginning = self.microtime_now()
            return False

        fps = self.fps  # frames per second

        microsecond = 10**6  # 1 second = 1*10^6 microseconds

        if time_end > time_beginning:
            time_variable = time_end - time_beginning
        else:
            time_variable = microsecond + time_end - time_beginning

        if time_variable > microsecond:
            # the code is going too slow, no wait
            self.key_read_timeout = 100
            self.game_time_beginning = self.microtime_now()
            return False

        frames_per_microsecond = int(microsecond/fps)

        pause = frames_per_microsecond - time_variable

        if pause < 0:
            # the code is going too slow, no wait
            self.key_read_timeout = 100
            self.game_time_beginning = self.microtime_now()
            return False

        # actively adjust the key reading timeout
        self.key_read_timeout = int(pause/10)

        # sleep
        time.sleep(pause/microsecond)

        # get the time from the beginning of the code
        self.game_time_beginning = self.microtime_now()

        return True

    def clear_screen(self):
        """Clears the screen

        It will detect the current operation system and choose which system
        screen clear function to use.
        """
        os_variable = self.os_variable

        # check which os the host is running
        if os_variable is None:
            if os.name == 'nt':
                # windows
                self.os_variable = 'windows'
            else:
                # other (linux)
                self.os_variable = 'other'

            os_variable = self.os_variable

        # clear the screen
        if os_variable == 'windows':
            # windows
            os.system('cls')
        else:
            # other (linux)
            os.system('clear')

    def read_key_press(self):
        """Returns the key character typed

        Can cause high CPU usage.
        Timeout variable will be auto updated by the fps_sync function.
        """
        self.modify_tty()
        timeout = self.key_read_timeout  # microseconds
        microsecond = 10**6  # 1 second = 1*10^6 microseconds

        # set the timeout variable if it has not already been set
        if timeout is None:
            timeout = 200*10**3  # recommended value
            self.key_read_timeout = timeout

        stdin = sys.stdin
        read = [stdin]
        read_timeout = timeout/microsecond  # timeout variable in seconds

        # check if any key is pressed within the timeout period
        rlist, wlist, xlist = select.select(read, [], [], read_timeout)
        if len(rlist) == 0:
            return None

        # return the key pressed
        return stdin.read(1)

    def modify_tty(self):
        tty_settings = self.tty_settings

        if tty_settings is not None:
            return False

        # save current tty config
        command = ['stty', '-g']
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        tty_settings = output.decode('ascii')
        self.tty_settings = tty_settings

        # change tty to be able to read in characters
        os.system('stty -icanon')

        return True

    def reset_tty(self):
        tty_settings = self.tty_settings

        if tty_settings is None:
            return False

        # reset tty back to its original state
        tty_settings = tty_settings.rstrip()
        os.system("stty '"+tty_settings+"'")

        return True


# init

engine = PyGameEngine()


# settings

frames_per_second_horizontal = 16
diff_constant = .65

engine.fps_horizontal = frames_per_second_horizontal
engine.fps_factor = diff_constant
engine.fps_vertical = int(engine.fps_horizontal*engine.fps_factor)
engine.fps = engine.fps_horizontal

point_dot = None

snake_sprite = '&'
right_pointing_triangle_sprite = '>'


# global variables

board_x = 80
board_y = 24
score = 0
snake_len = 0
snake_old_len = 0
total_number_of_frames = 0
increase_interval = 1
global_game_title = snake_sprite+' Py Snake '+right_pointing_triangle_sprite
key = None
left_margin = ' '
screen = None
blank_board = {}
do_increase_player = False
update_point_dot = False
dev_mode = False


# game setup (to be run once)

# create the background and frame wall
background = create_background()
frame_wall = create_frame_wall()

# draw the background and frame onto the board and store it in the draw cache
cache_draw = True
draw([
    background,
    frame_wall
])

# create the player
player = create_player()


# game loop
while True:
    # add stats to the screen
    screen = print_stats()

    # update the player
    player = player_function(player)

    # update the point dot
    point_dot = point_dot_function(player, point_dot)

    # collision testing
    collision_testing(player, point_dot)

    # draw the board with all the entities on it and add it to the screen
    board = draw([
        point_dot,
        player
    ])
    screen += board

    # clear the screen
    engine.clear_screen()

    # print the screen
    print(screen)

    # take key input
    print(left_margin)
    key = engine.read_key_press()

    # perform key actions
    key_actions()

    # count frames
    total_number_of_frames += 1

    # sync game loop to the saved fps value
    engine.fps_sync()
