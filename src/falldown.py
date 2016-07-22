#!/usr/bin/python2

#############################################################################
# Copyright 2016 Mass KonFuzion Games
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#############################################################################


import pygame
import sys
import math

from game_application import GameApplication
import game_state_intro

def main():
    # NOTE: Couldn't decide whether to put pygame.init() at this level or in the GameApplication class. It probably belongs in GameApplication (in an Init()) function of sorts..)
    pygame.init()

    game = GameApplication()
    game.changeState(game_state_intro.GameStateImpl.Instance())

    # NOTE timer should be part of application class, too, but this is hack'n'slash.. No time to fix it!!
    prev_time = pygame.time.get_ticks()

    while game.isRunning:
        curr_time = pygame.time.get_ticks()
        dt_s = (curr_time - prev_time) / 1000.0
        #print "Curr {}, prev {}, dt {}".format(curr_time, prev_time, dt_s)
        prev_time = curr_time

        # ----- Process events
        game.processEvents()

        # ----- Process commands
        game.processCommands()

        # ----- Update stuff
        game.update(dt_s, game.cell_size)

        # ----- pre-render 
        game.preRenderScene()

        # ----- Draw stuff
        game.renderScene()

        # ----- post-render (e.g. score/overlays)
        game.postRenderScene()

    # Do any engine cleanup here

if __name__ == '__main__':
    main()
