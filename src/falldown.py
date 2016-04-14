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

def initLevel(row_mgr, num_rows, update_delay, reInitCell, cell_size):
    # TODO Make the following updates:
    # - change num_rows to row_spacing. or something.
    # - Generate rows so that row spacing is consistent all the way down the screen. Mimic scenario where, if spacing is 10, then 7 rows are created (i.e., there's a row created off-screen, at cell 70, to keep spacing consistent on reInit. The goal is to make sure that the spacing of all rows on the screen is ALWAYS the same; so make enough rows to ensure that
    # - And lastly, compute the reInitCell - the cell position where each row should be reInitialized at when a row goes above the top edge of the screen (and make sure it gets returned to the main function.. Perhaps store these properties in a dict or some other object that Python will pass to the function as a reference)
    # - Make sure this initLevel function is smart enough to add new rows to the row list when necessary, and to otherwise reInit rows when it's not necessary to add new rows to the list. Maybe make the function dumb, and have the prorammer specify it in the function call? Or otherwise, have the function compute the number of rows necessary to keep the row spacing even, and add new rows as necessary.
    # TODO actually.. initLevel should belong to the row manager.. That's the entire point

    #for i in xrange(0, num_rows):
    if True: # Putting in a BS conditional just to keep indent levels the same. Next project should be to move the initLevel function into the row manager
        row_mgr.createRowAndAddToRowList(yPosition=10, updateDelay=update_delay, cellSize = cell_size)
        row_mgr.createRowAndAddToRowList(yPosition=20, updateDelay=update_delay, cellSize = cell_size)
        row_mgr.createRowAndAddToRowList(yPosition=30, updateDelay=update_delay, cellSize = cell_size)
        row_mgr.createRowAndAddToRowList(yPosition=40, updateDelay=update_delay, cellSize = cell_size)
        row_mgr.createRowAndAddToRowList(yPosition=50, updateDelay=update_delay, cellSize = cell_size)
        row_mgr.createRowAndAddToRowList(yPosition=60, updateDelay=update_delay, cellSize = cell_size)
        row_mgr.createRowAndAddToRowList(yPosition=70, updateDelay=update_delay, cellSize = cell_size)

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
    ball.setPosition(10, 10) # Position is given in coordinates on the 64x64 grid. Actual screen coordinates are calculated from grid coordinates
    ball.setSpeed(0,1)
    ball.setMaxSpeed(1,1)

    scoredFlag = False # Flag that tells whether player has scored or not # TODO make scorekeeping/game event management more robust
    score = 0
    GAP_SCORE = 10  # NOTE Scoring elements could be managed by a class/object. But whatever, no time!

    #rowReInitGridCell = 0       # Grid cell where new rows will be added (more accurately, where they'll be re-initialized)
    initialRowUpdateDelay = 1
    initialNumRows = 7
    #initialSpacingBetweenRows = 10



    rm = RowManager()
    initLevel(rm, initialNumRows, initialRowUpdateDelay, 70, cell_size) 
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
                            # TODO add score keeping
                            if ball.getGameState() != BallGameState.FREEFALL:
                                ball.changeGameState(BallGameState.FREEFALL)
                                scoredFlag = True
                                print "Changing ball game state to FREEFALL"

                        elif geom._type == Row.COLLISION_TYPE_ROW:
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
                            if ball.getGameState() != BallGameState.ON_ROW and ball._lastContactRow != i:
                                ball.changeGameState(BallGameState.ON_ROW)
                                ball._lastContactRow = i
                                print "Changing ball game state to ON_ROW"

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
            #print "Jyeaw! Score!"
            score += GAP_SCORE # GAP_SCORE can increase as the difficulty level increases
            scoredFlag = False
        
        #for i in range(0, ball.getGameState()):
        #    print "BallGameState:{}".format(ball.getGameState()),
        #print

        
        pygame.display.flip()

        ## The stuff between here and tne __name__ test is debug stuff. You can delete it once the bugs are worked out

if __name__ == '__main__':
    main()
