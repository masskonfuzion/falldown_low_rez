#!/usr/bin/python2

import pygame
import sys
import math

from game_application import GameApplication
import game_state_intro

def main():
    # TODO add game states (e.g. intro, playing, menu, etc)
    # TODO add scoring / game logic
    #   Ideas:
    #   Game requires fierce tapping to move (instead of auto move)
    #   Game can include powerups (e.g., auto-move; warp)
    #   Game evaluates difficulty and how "nice" it's been to you; e.g. game knows how many rows are on screen; where you are on screen; when it last gave you a powerup; etc. Judge when to dole out powerups based on that
    #   Scorekeeping requires detecting collisions with a row's gap

    # TODO Put pygame.init() into the GameApplication class?
    pygame.init()

    game = GameApplication()

	# TODO make sure to change state to the Intro State
    game.changeState(game_state_intro.GameStateIntro.Instance())

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
        # TODO make accessor functions for every _xyz member? e.g., instead of ball._position, make ball.getPosition()?

        # Get collisions (note - here, we're using specialized logic. For a more generic game engine, we would need to do more work here. But, we're purpose-building the "engine" for this game, sooo whatever :-D

        # NOTE To properly evaluate scoring logic, we need to know which row the ball is touching. We can either add a data member to the row object or otherwise use a counter loop, rather than an iterator. We chose the counter loop
        game.preRenderScene()

        # ----- Draw stuff
        game.renderScene()

        # ----- post-render (e.g. score/overlays)
        game.postRenderScene()

    # TODO do any engine cleanup


if __name__ == '__main__':
    main()
