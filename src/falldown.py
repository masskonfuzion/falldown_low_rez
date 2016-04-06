#!/usr/bin/python2

import pygame
import sys


# Import game objects (perhaps this can go into a "game manager" of some sort?)
from ball import Ball

def main():
    pygame.init()

    # dirt-nasty initialization: screen_size is a tuple (width, height); width, height is initialized as 640x640
    screen_size = width, height = 640, 640
    cell_size = width / 64, height / 64 # recompute this if screen size changes
    #screen_size = width, height = 854, 640 # The playable area will be a 640 x 640 square.
    screen = pygame.display.set_mode(screen_size)

    bg_col = 255,255,255

    # TODO rename ball; add it to a list of game objects. e.g. [ ball, [ rows ] ], or maybe even better: [ ball, row_mgr ] (where row_mgr contains rows)
    a = Ball()
    a.setPosition(10, 10)
    a.setSpeed(0,1)

    prev_time = pygame.time.get_ticks()
    while True:
        curr_time = pygame.time.get_ticks()
        dt_s = (curr_time - prev_time) / 1000.0
        #print "Curr {}, prev {}, dt {}".format(curr_time, prev_time, dt_s)
        prev_time = curr_time

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


        # Update stuff
        a.update(dt_s, cell_size)

        # pre-render (e.g. constrain ball to screen space)
        # TODO make accessor functions for every _xyz member? e.g., instead of a._position, make a.getPosition()?
        # TODO put constraints into function?
        for i in range(0, 2):
            if a._position[i] < 0:
                a._position[i] = 0
            if a._position[i] > 63:
                a._position[i] = 63

        # Draw stuff
        screen.fill(bg_col)
        a.draw(screen, cell_size)

        # post-render (e.g. score/overlays)

        
        pygame.display.flip()

if __name__ == '__main__':
    main()
