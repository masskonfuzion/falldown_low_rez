#!/usr/bin/python2

import pygame
import sys


# Import game objects (perhaps this can go into a "game manager" of some sort?)
from ball import Ball
from row import Row
from row_manager import RowManager

# TODO: For scorekeeping, keep track of ball's last contact? e.g., with_row, with_boundary, something like that? That way, we can know when the ball fall through a hole, and give points. Give bonuses for touching the bottom of the screen

def drawGrid(screen, cell_size, screen_size):
    for i in range(0, 63):
        color = 192, 192, 192
        pygame.draw.line(screen, color, ( (i + 1) * cell_size[0], 0                      ), ( (i + 1) * cell_size[1], screen_size[1]         ) )
        pygame.draw.line(screen, color, ( 0                     , (i + 1) * cell_size[0] ), ( screen_size[1]        , (i + 1) * cell_size[1] ) )

def main():
    pygame.init()

    # dirt-nasty initialization: screen_size is a tuple (width, height); width, height is initialized as 640x640
    screen_size = width, height = 640, 640
    #screen_size = width, height = 854, 640 # The playable area will be a 640 x 640 square.
    cell_size = width / 64, height / 64 # cell size (starts off as 10px x 10px. recompute this if screen size changes)
    screen = pygame.display.set_mode(screen_size)

    bg_col = 255,255,255

    # TODO rename ball; add it to a list of game objects. e.g. [ ball, [ rows ] ], or maybe even better: [ ball, row_mgr ] (where row_mgr contains rows)
    a = Ball()
    a.setPosition(10, 10) # Position is given in coordinates on the 64x64 grid. Actual screen coordinates are calculated from grid coordinates
    a.setSpeed(0,1)
    a.setMaxSpeed(1,1)

    #TODO delete references to individual row.
    #r = Row()
    #r.setPosition(0, 32)
    #r._gap = 5

    rm = RowManager()
    rm.createRowAndAddToRowList(yPosition=20)
    rm.createRowAndAddToRowList(yPosition=30)
    rm.createRowAndAddToRowList(yPosition=40)

    prev_time = pygame.time.get_ticks()
    while True:
        curr_time = pygame.time.get_ticks()
        dt_s = (curr_time - prev_time) / 1000.0
        #print "Curr {}, prev {}, dt {}".format(curr_time, prev_time, dt_s)
        prev_time = curr_time

        # ----- Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
				# NOTE!!!! In a better-designed game, this keydown event would put a message on a message queue, which a destination of "Ball" or whatever. Then, the ball, which is listening to the queue, gets the message
                ballRef = a     # Set a reference to the ball (NOTE: Later on, we'll want to refer to something else, either an item in a array or some other such thing)

                # Left arrow key
                if (event.key == pygame.K_LEFT or event.key == pygame.K_j):
                    ballRef.controlState.setLeftKeyPressedTrue()
                # Right arrow key
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_l):
                    ballRef.controlState.setRightKeyPressedTrue()
            elif event.type == pygame.KEYUP:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_j):
                    ballRef.controlState.setLeftKeyPressedFalse()
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_l):
                    ballRef.controlState.setRightKeyPressedFalse()

        # ----- Update stuff
        a.update(dt_s, cell_size)
        rm.update(dt_s, cell_size)

        # ----- pre-render 
        # TODO make accessor functions for every _xyz member? e.g., instead of a._position, make a.getPosition()?

        # Get collisions (note - here, we're using specialized logic. For a more generic game engine, we would need to do more work here. But, we're purpose-building the "engine" for this game, sooo whatever :-D
        # There can only ever be 1 collision/contact in this game..
        # O(n^2)... terrible
        for row in rm._rows:
            for geom in row._collGeoms:
                if geom:
                    if geom.isColliding(a._collGeoms[0], cell_size):
                        # TODO make positioning more robust. If ball is falling through blocks, and touches side of blocks, e.g., then 'clamp' it to the side of the blocks, and not the top
                        a.setPosition(a._position[0], geom._position[1] - a._size[1])

        # (e.g. constrain ball to screen space)
        # TODO put constraints into function?
        for i in range(0, 2):
            if a._position[i] < 0:
                a._position[i] = 0
            if a._position[i] + a._size[i] > 64:
                a._position[i] = 64 - a._size[i]

        # ----- Draw stuff
        screen.fill(bg_col)

        drawGrid(screen, cell_size, screen_size)
        a.draw(screen, cell_size)
        #r.draw(screen, cell_size) #TODO delete references to individual row.
        rm.draw(screen, cell_size)

        # ----- post-render (e.g. score/overlays)

        
        pygame.display.flip()

        ## The stuff between here and tne __name__ test is debug stuff. You can delete it once the bugs are worked out

if __name__ == '__main__':
    main()
