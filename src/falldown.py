#!/usr/bin/python2

import pygame
import sys
import math


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
                    # TODO: Rename the ball. It shouldn't be called "a"
                    if geom.isColliding(a._collGeoms[0], cell_size):
                        # Compute the collision normal (from the center of one AABB to the center of the other. Note: this is what a true contract resolution system should be doing)
                        # NOTE: Here, we're going to use the RENDER geometry to calculate a higher-resolution normal than would be posslble with just the pure grid positions of each object
                        
                        # This is the ball render rect: my_rect = (self._position[0] * cell_size[0], self._position[1] * cell_size[1], self._size[0] * cell_size[0], self._size[1] * cell_size[1])
                        # Compute the center point
                        ##ballCenter = [ int(self._position[0] * cell_size[0] + (self._size[0] * cell_size[0] / 2)), int(self._position[1] * cell_size[1] + (self._size[1] * cell_size[1]) / 2) ]
                        ##geomCenter = [ geom._minPt[0] + (geom._maxPt[0] - geom._minPt[0]) / 2, geom._minPt[1] + (geom._maxPt[1] - geom._minPt[1]) / 2 ]

                        ####### TODO TODO TODO TODO TODO! Calculate the collision normal using the collision geoms' position. This means we have to make the collision geoms' positioning more robust
                        # NOTE: Geom position is now computed in terms of 64x64 grid. Now we have positions of the ball and the geoms the grid. Now we need to compute the contact normal using those positions
                        # TODO: Fix this computation. Don't calculate in terms of screen coordinates.





                        # TODO - fix normal calculation (i.e., AABB sizes, positions, ball size/position, etc.. Something is off; it's not properly computing the center points)



                        # Multiply by 0.5 to force Python to convert the numbers from int to float
                        ballCenter = [ a._position[0] + a._size[0] * 0.5, a._position[1] + a._size[1] * 0.5 ]
                        geomCenter = [ geom._position[0] + geom._size[0] * 0.5, geom._position[1] + geom._size[1] * 0.5 ]

                        # This is a straight-up vector subtraction. No vector class needed :-) We're taking madd shortcuts
                        contactNormal = [ ballCenter[0] - geomCenter[0], ballCenter[1] - geomCenter[1] ]

                        #cnLen = math.sqrt(contactNormal[0] * contactNormal[0] + contactNormal[1] * contactNormal[1])
                        #cnNormalized = [ contactNormal[0] / cnLen, contactNormal[1] / cnLen ]

                        #print "Contact normal:{} cnNormalized:{} ballCenter:{} geomCenter:{}".format(contactNormal, cnNormalized, ballCenter, geomCenter)
                        print "Contact normal:{} ballCenter:{} geomCenter:{}".format(contactNormal, ballCenter, geomCenter)

                        # At this point, we know we're colliding already, so we can calculate the penetration depths along each AABB axis
                        penDepth = [ a._collGeoms[0]._maxPt[0] - geom._minPt[0], a._collGeoms[0]._maxPt[1] - geom._minPt[1] ] 

                        correctionVector = [0, 0]

                        if abs(penDepth[0]) < abs(penDepth[1]):
                            correctionVector[0] = -penDepth[0] / cell_size[0]
                        else:
                            correctionVector[1] = -penDepth[1] / cell_size[1]

                        a.setPosition( a._position[0] + correctionVector[0], a._position[1] + correctionVector[1] )
                        a._computeCollisionGeometry(cell_size) # NOTE: the ball should recompute its geometry on a setPosition() call. Perhaps a fn override is needed (right now, setPosition is part of base class)

                        # TODO make positioning more robust. If ball is falling through blocks, and touches side of blocks, e.g., then 'clamp' it to the side of the blocks, and not the top
                        #a.setPosition(a._position[0], geom._position[1] - a._size[1])
                        # Now that we have a contact normal, we need to push the ball back out so it is not penetrating the row AABB, but clamp that movement to the grid

                        # Note: The following draw statements will be invisible unless you also disable screen filling in the draw() fn. But then, the screen won't clear, and you'll have a trail
                        #pygame.draw.circle(screen, (128,0,0), (int(ballCenter[0] * cell_size[0]), int(ballCenter[1] * cell_size[1])), 16, 2)
                        #pygame.draw.circle(screen, (128,0,128), (int(geomCenter[0] * cell_size[0]), int(geomCenter[1] * cell_size[1])), 16, 2)


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
