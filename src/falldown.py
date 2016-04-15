#!/usr/bin/python2

import pygame
import sys
import math


# Import game objects (perhaps this can go into a "game manager" of some sort?)
from ball import Ball
from row import Row
from row_manager import RowManager
from ball_game_state import BallGameState

# TODO: For scorekeeping, keep track of ball's last contact? e.g., with_row, with_boundary, something like that? That way, we can know when the ball fall through a hole, and give points. Give bonuses for touching the bottom of the screen

class DaGame:
    ''' Application class that stores all the data and stuff
    '''
    def __init__(self):
        pass

def drawGrid(screen, cell_size, screen_size):
    for i in range(0, 63):
        color = 192, 192, 192
        pygame.draw.line(screen, color, ( (i + 1) * cell_size[0], 0                      ), ( (i + 1) * cell_size[1], screen_size[1]         ) )
        pygame.draw.line(screen, color, ( 0                     , (i + 1) * cell_size[0] ), ( screen_size[1]        , (i + 1) * cell_size[1] ) )


def main():
    # TODO add game states (e.g. intro, playing, menu, etc)
    # TODO add scoring / game logic
    #   Ideas:
    #   Game requires fierce tapping to move (instead of auto move)
    #   Game can include powerups (e.g., auto-move; warp)
    #   Game evaluates difficulty and how "nice" it's been to you; e.g. game knows how many rows are on screen; where you are on screen; when it last gave you a powerup; etc. Judge when to dole out powerups based on that
    #   Scorekeeping requires detecting collisions with a row's gap

    pygame.init()

    # dirt-nasty initialization: screen_size is a tuple (width, height); width, height is initialized as 640x640
    screen_size = width, height = 640, 640
    #screen_size = width, height = 854, 640 # The playable area will be a 640 x 640 square.
    cell_size = width / 64, height / 64 # cell size (starts off as 10px x 10px. recompute this if screen size changes)
    screen = pygame.display.set_mode(screen_size)

    bg_col = 255,255,255

    # TODO add ball to a list of game objects. e.g. [ ball, [ rows ] ], or maybe even better: [ ball, row_mgr ] (where row_mgr contains rows)
    ball = Ball()
    ball.setPosition(32, 0) # Position is given in coordinates on the 64x64 grid. Actual screen coordinates are calculated from grid coordinates
    ball.setSpeed(0,1)
    ball.setMaxSpeed(1,1)
    ball.changeGameState(BallGameState.FREEFALL)
    print "Changing ball game state to FREEFALL"

    scoredFlag = False # Flag that tells whether player has scored or not # TODO make scorekeeping/game event management more robust
    score = 0
    GAP_SCORE = 10  # NOTE Scoring elements could be managed by a class/object. But whatever, no time!

    #rowReInitGridCell = 0       # Grid cell where new rows will be added (more accurately, where they'll be re-initialized)
    initialRowUpdateDelay = 1
    initialNumRows = 7
    #initialSpacingBetweenRows = 10



    rm = RowManager()
    rm.initLevel(initialNumRows, initialRowUpdateDelay, 70, cell_size) 
    # TODO make sure the reInit call uses the reInitCell defined here (and for that matter, don't hardcode it here)
    # TODO actually.. initLevel should belong to the row manager.. That's the entire point


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
                ballRef = ball # Set a reference to the ball (NOTE: Later on, we'll want to refer to something else, either an item in a array or some other such thing)

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
        ball.update(dt_s, cell_size)
        rm.update(dt_s, cell_size)

        # ----- pre-render 
        # TODO make accessor functions for every _xyz member? e.g., instead of ball._position, make ball.getPosition()?

        # Get collisions (note - here, we're using specialized logic. For a more generic game engine, we would need to do more work here. But, we're purpose-building the "engine" for this game, sooo whatever :-D
        # There can only ever be 1 collision/contact in this game..
        # O(n^2)... terrible

        # NOTE To properly evaluate scoring logic, we need to know which row the ball is touching. We can either add a data member to the row object or otherwise use a counter loop, rather than an iterator. We chose the counter loop
        for i in xrange(0, len(rm._rows)):
            row = rm._rows[i]
            rowCollisionFound = False # Perhaps put this variable in a class/object? (Purpose of var is to stop testing collisions against all rows upon 1st collision)

            #print "DEBUG row={} gap={}".format(i, row._gap)
            #print "\tDEBUG row._collGeoms={}".format(row._collGeoms)

            # Test rows going off the screen
            if row._position[1] + row._size[1] / 2 == 0:
                #row.reInit(64 - row._size[1] / 2, -1)  # TODO Consider not hardcoding gap to -1; Allow "levels" with pre-determined gap sequences
                row.reInit(70 - row._size[1] / 2, -1)  # TODO decide what to do with new rows.. starting at 70 works if we're starting new rows every 10 grid cells. Figure out how to compute
                # NOTE render geom and collision geom are not recomputed until the next update(). But it's ok; at this point in time, the row is off the screen

            # Test collisions
            for geom in row._collGeoms:
                if geom:
                    # NOTE: We need to test for collision with a gap first, then check for the row, because the ball can possibly be in contact with both the row and gap at the same time. That way, we can be sure that we're clearly on a gap if the ball is in contact with the gap but not the row at the same time.
                    # TODO remove cell_size from the isColliding call
                    if geom.isColliding(ball._collGeoms[0], cell_size):
                        if geom._type == Row.COLLISION_TYPE_GAP:
                            #print "\t\tDEBUG gap collision! ball geom={} row geom={}".format(row._collGeoms[0], geom)
                            if ball.getGameState() != BallGameState.FREEFALL:
                                ball.changeGameState(BallGameState.FREEFALL)
                                print "Changing ball game state to FREEFALL"

                            # TODO add score keeping
                            if ball._lastRowScored != i: 
                                ball._lastRowScored = i 
                                scoredFlag = True # This flag could also be handled as a message from the ball or row or whatever, to the game logic (in a better designed game), to trigger the game logic's score handler

                        elif geom._type == Row.COLLISION_TYPE_ROW:
                            #print "\t\tDEBUG row collision! ball geom={} row geom={}".format(row._collGeoms[0], geom)
                            # Compute the collision normal (from the center of one AABB to the center of the other. Note: this is what a true contract resolution system should be doing)
                            # Multiply by 0.5 to force Python to convert the numbers from int to float
                            ballCenter = [ ball._position[0] + ball._size[0] * 0.5, ball._position[1] + ball._size[1] * 0.5 ]
                            geomCenter = [ geom._position[0] + geom._size[0] * 0.5, geom._position[1] + geom._size[1] * 0.5 ]

                            # This is a straight-up vector subtraction. No vector class needed :-) We're taking madd shortcuts
                            contactNormal = [ ballCenter[0] - geomCenter[0], ballCenter[1] - geomCenter[1] ]

                            # At this point, we know we're colliding already, so we can calculate the penetration depths along each AABB axis
                            penDepth = [ ball._collGeoms[0]._maxPt[0] - geom._minPt[0], ball._collGeoms[0]._maxPt[1] - geom._minPt[1] ] 

                            correctionVector = [0, 0]

                            if abs(penDepth[0]) < abs(penDepth[1]):
                                correctionVector[0] = -penDepth[0] / cell_size[0]
                            else:
                                correctionVector[1] = -penDepth[1] / cell_size[1]

                            ball.setPosition( ball._position[0] + correctionVector[0], ball._position[1] + correctionVector[1] )
                            ball._computeCollisionGeometry(cell_size) # NOTE: the ball should recompute its geometry on a setPosition() call. Perhaps a fn override is needed (right now, setPosition is part of base class)
                            ball.resetUpdateDelay()

                            # Note: The following draw statements will be invisible unless you also disable screen filling in the draw() fn. But then, the screen won't clear, and you'll have a trail
                            #pygame.draw.circle(screen, (128,0,0), (int(ballCenter[0] * cell_size[0]), int(ballCenter[1] * cell_size[1])), 16, 2)
                            #pygame.draw.circle(screen, (128,0,128), (int(geomCenter[0] * cell_size[0]), int(geomCenter[1] * cell_size[1])), 16, 2)

                            # Change gamestate of ball
                            if ball.getGameState() != BallGameState.ON_ROW and ball._lastRowTouched != i:
                                ball.changeGameState(BallGameState.ON_ROW)
                                ball._lastRowTouched = i
                                print "Changing ball game state to ON_ROW"

                        rowCollisionFound = True
                        break # break out of for loop if we have a collision

                    #else:
                    #    # If no row collisions were found at all, then we must be in freefall
                    #    #print "\t\tDEBUG no collision! ball geom={} row geom={}".format(row._collGeoms[0], geom)
                    #    if ball.getGameState() != BallGameState.FREEFALL:
                    #        ball.changeGameState(BallGameState.FREEFALL)
                    #        print "Changing ball game state to FREEFALL"

            if rowCollisionFound:
                # If we found a collision against any row, we can stop testing for any collisions, because we're done. Reset the flag and _exit all for loops_
                rowCollisionFound = False
                break

        #print # blank line



        # (e.g. constrain ball to screen space)
        # TODO put constraints into function?
        for i in range(0, 2):
            if ball._position[i] < 0:
                ball._position[i] = 0
            if ball._position[i] + ball._size[i] > 64:
                ball._position[i] = 64 - ball._size[i]

            # TODO Add a ball game state here? Right now, if the ball reaches the bottom of the screen, it's considered 'freefall' because there's nothing that sets the ball game state to anything else

        # ----- Draw stuff
        screen.fill(bg_col)

        drawGrid(screen, cell_size, screen_size)
        ball.draw(screen, cell_size)
        rm.draw(screen, cell_size)

        # ----- post-render (e.g. score/overlays)
        # If ball state is FREEFALL at this point, then we can register a score
        if scoredFlag:
            print "Jyeaw! Score"
            score += GAP_SCORE # GAP_SCORE can increase as the difficulty level increases
            scoredFlag = False
        
        #for i in range(0, ball.getGameState()):
        #    print "BallGameState:{}".format(ball.getGameState()),
        #print

        
        pygame.display.flip()

        ## The stuff between here and tne __name__ test is debug stuff. You can delete it once the bugs are worked out

if __name__ == '__main__':
    main()
