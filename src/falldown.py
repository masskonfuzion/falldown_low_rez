#!/usr/bin/python2

import pygame
import sys
import math

# Import game objects (perhaps this can go into a "game manager" of some sort?)
from ball import Ball
from row import Row
from row_manager import RowManager
from ball_game_state import BallGameState
from display_msg import DisplayMessage
from display_msg_manager import DisplayMessageManager


class GameApplication(object):
    ''' Application class that stores all the data and stuff
    '''
    def __init__(self):
        ''' Application class
        '''
        # dirt-nasty initialization: screen_size is a tuple (width, height); width, height is initialized as 640x640
        self.game_size = [640, 640]
        self.screen_size = [854, 640] # The playable area will be a 640 x 640 square.
        self.cell_size = [self.game_size[0] / 64, self.game_size[1] / 64] # cell size (starts off as 10px x 10px. recompute this if screen size changes)
        self.surface_bg = pygame.display.set_mode(self.screen_size)
        self.game_viewport = pygame.Surface((640, 640))

        self.bg_col = 255,255,255
        self.scoredFlag = False # Flag that tells whether player has scored or not # TODO make scorekeeping/game event management more robust
        self.score = 0
        self.GAP_SCORE = 10  # NOTE Scoring elements could be managed by a class/object. But whatever, no time!
        self.tries = 3   # We're calling them "tries" because "lives" doesn't make sense for a ball :-D

        self._gotCrushed = False
        self._gameState = "Playing"

        self.initialRowUpdateDelay = .5
        self.initialRowSpacing = 4
        self._lastDifficultyIncreaseScore = 0

        # TODO add ball to a list of game objects. e.g. [ ball, [ rows ] ], or maybe even better: [ ball, row_mgr ] (where row_mgr contains rows)
        self.ball = Ball()
        self.ball._accumulator_s[1] = 0.0
        self.ball.setPosition(32, 0) # Position is given in coordinates on the 64x64 grid. Actual screen coordinates are calculated from grid coordinates
        self.ball.setSpeed(0,1)
        self.ball.setMaxSpeed(1,1)
        self.ball.changeGameState(BallGameState.FREEFALL)
        #print "Changing ball game state to FREEFALL"

        self.mm = DisplayMessageManager()

        self.rm = RowManager()
        self.rm.initLevel(self.initialRowSpacing, self.initialRowUpdateDelay, self.cell_size) 

        self.displayMsgScore = DisplayMessage()
        self.displayMsgScore.create(txtStr="Score: ", position=[66, 5], color=(192,192,192))

        self.displayMsgTries = DisplayMessage()
        self.displayMsgTries.create(txtStr="Tries: ", position=[66, 10], color=(192,192,192))
    
        self.displayMsgCrushed = DisplayMessage()
        self.displayMsgCrushed.create(txtStr="Crushed :-(", position=[66, 20], color=(192,192,192))
    
        self.displayMsgGameOver = DisplayMessage()
        self.displayMsgGameOver.create(txtStr="GameOver :-(", position=[66, 32], color=(192,192,192))

    def drawGrid(self, screen, cell_size, screen_size):
        for i in range(0, 63):
            color = 192, 192, 192
            pygame.draw.line(screen, color, ( (i + 1) * cell_size[0], 0                      ), ( (i + 1) * cell_size[1], screen_size[1]         ) )
            pygame.draw.line(screen, color, ( 0                     , (i + 1) * cell_size[0] ), ( screen_size[1]        , (i + 1) * cell_size[1] ) )

    def update(self, dt_s, cell_size):
        # HORRENDOUS state mgmt style here. Use State Pattern instead
        if self._gameState == "Playing":
            self.ball.update(dt_s, cell_size)
            self.rm.update(dt_s, cell_size)
            self.mm.update(dt_s, cell_size)

            self.updateDifficulty()

    def processEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            # TERRIBLE state mgmt style here
            if self._gameState == "Playing":
                if event.type == pygame.KEYDOWN:
			    	# NOTE!!!! In a better-designed game, this keydown event would put a message on a message queue, which a destination of "Ball" or whatever. Then, the ball, which is listening to the queue, gets the message

                    # Left arrow key
                    if (event.key == pygame.K_LEFT or event.key == pygame.K_j):
                        self.ball.controlState.setLeftKeyPressedTrue()
                    # Right arrow key
                    elif (event.key == pygame.K_RIGHT or event.key == pygame.K_l):
                        self.ball.controlState.setRightKeyPressedTrue()
                elif event.type == pygame.KEYUP:
                    if (event.key == pygame.K_LEFT or event.key == pygame.K_j):
                        self.ball.controlState.setLeftKeyPressedFalse()
                    elif (event.key == pygame.K_RIGHT or event.key == pygame.K_l):
                        self.ball.controlState.setRightKeyPressedFalse()

            elif self._gameState == "Crushed":
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RETURN:
                        self.tries -= 1

                        if self.tries > 0:
                            self._gameState = "Playing"
                        else:
                            self._gameState = "GameOver"

                        # Super janky way of resetting the ball. Running out of time
                        self.ball._accumulator_s[1] = 0.0
                        self.ball.setPosition(32, 0) # Position is given in coordinates on the 64x64 grid. Actual screen coordinates are calculated from grid coordinates
                        self.ball.setSpeed(0,1)
                        self.ball.setMaxSpeed(1,1)
                        self.ball.changeGameState(BallGameState.FREEFALL)

                        self.rm.initLevel(self.initialRowSpacing, self.initialRowUpdateDelay, self.cell_size) 


            elif self._gameState == "GameOver":
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        sys.exit()



    def enforceConstraints(self):
        # (e.g. constrain ball to screen space)
        # TODO put constraints into function?
        for i in range(0, 2):
            if self.ball._position[i] < 0:
                self.ball._position[i] = 0
                if i == 1:
                    self._gotCrushed = True
                    self._gameState = "Crushed"

            if self.ball._position[i] + self.ball._size[i] > 64:
                self.ball._position[i] = 64 - self.ball._size[i]

            # TODO Add a ball game state here? Right now, if the ball reaches the bottom of the screen, it's considered 'freefall' because there's nothing that sets the ball game state to anything else


    def updateDifficulty(self):
        # Some hard-coded stuff here -- would like to make a more robust level management system, but I'm scrambling to meet the submission deadline for Low Rez Jam 2016. Maybe I'll update later
        if self.score % 100 == 0 and self._lastDifficultyIncreaseScore < self.score:
            self._lastDifficultyIncreaseScore = self.score
            self.rm.changeUpdateDelay(self.rm._updateDelay - 0.1)
            self.mm.setMessage("Level Up!".format(self.GAP_SCORE), [ self.ball._position[0], self.ball._position[1] - self.ball._size[1] ], (192, 64, 64), 8 )
            #self.rm.reInitLevel(self.rm._rowSpacing - 1, self.rm._updateDelay - 0.1, self.cell_size) 


    def doCollisions(self):
        # There can only ever be 1 collision/contact in this game..
        # O(n^2)... terrible

        for i in xrange(0, len(self.rm._rows)):
            row = self.rm._rows[i]
            rowCollisionFound = False # Perhaps put this variable in a class/object? (Purpose of var is to stop testing collisions against all rows upon 1st collision)

            #print "DEBUG row={} gap={}".format(i, row._gap)
            #print "\tDEBUG row._collGeoms={}".format(row._collGeoms)

            # Test collisions
            for geom in row._collGeoms:
                if geom:
                    # NOTE: We need to test for collision with a gap first, then check for the row, because the ball can possibly be in contact with both the row and gap at the same time. That way, we can be sure that we're clearly on a gap if the ball is in contact with the gap but not the row at the same time.
                    # TODO remove cell_size from the isColliding call
                    if geom.isColliding(self.ball._collGeoms[0], self.cell_size):
                        if geom._type == Row.COLLISION_TYPE_GAP:
                            #print "\t\tDEBUG gap collision! ball geom={} row geom={}".format(row._collGeoms[0], geom)
                            if self.ball.getGameState() != BallGameState.FREEFALL:
                                self.ball.changeGameState(BallGameState.FREEFALL)
                                #print "Changing ball game state to FREEFALL"

                            if self.ball._lastRowScored != i: 
                                self.ball._lastRowScored = i 
                                self.scoredFlag = True # This flag could also be handled as a message from the ball or row or whatever, to the game logic (in a better designed game), to trigger the game logic's score handler

                        elif geom._type == Row.COLLISION_TYPE_ROW:
                            #print "\t\tDEBUG row collision! ball geom={} row geom={}".format(row._collGeoms[0], geom)
                            # Compute the collision normal (from the center of one AABB to the center of the other. Note: this is what a true contract resolution system should be doing)
                            # Multiply by 0.5 to force Python to convert the numbers from int to float
                            ballCenter = [ self.ball._position[0] + self.ball._size[0] * 0.5, self.ball._position[1] + self.ball._size[1] * 0.5 ]
                            geomCenter = [ geom._position[0] + geom._size[0] * 0.5, geom._position[1] + geom._size[1] * 0.5 ]

                            # This is a straight-up vector subtraction. No vector class needed :-) We're taking madd shortcuts
                            contactNormal = [ ballCenter[0] - geomCenter[0], ballCenter[1] - geomCenter[1] ]

                            # At this point, we know we're colliding already, so we can calculate the penetration depths along each AABB axis
                            penDepth = [ self.ball._collGeoms[0]._maxPt[0] - geom._minPt[0], self.ball._collGeoms[0]._maxPt[1] - geom._minPt[1] ] 

                            correctionVector = [0, 0]

                            if abs(penDepth[0]) < abs(penDepth[1]):
                                correctionVector[0] = -penDepth[0] / self.cell_size[0]
                            else:
                                correctionVector[1] = -penDepth[1] / self.cell_size[1]

                            self.ball.setPosition( self.ball._position[0] + correctionVector[0], self.ball._position[1] + correctionVector[1] )
                            self.ball._computeCollisionGeometry(self.cell_size) # NOTE: the ball should recompute its geometry on a setPosition() call. Perhaps a fn override is needed (right now, setPosition is part of base class)
                            self.ball.resetUpdateDelay()

                            # Note: The following draw statements will be invisible unless you also disable screen filling in the draw() fn. But then, the screen won't clear, and you'll have a trail
                            #pygame.draw.circle(screen, (128,0,0), (int(ballCenter[0] * cell_size[0]), int(ballCenter[1] * cell_size[1])), 16, 2)
                            #pygame.draw.circle(screen, (128,0,128), (int(geomCenter[0] * cell_size[0]), int(geomCenter[1] * cell_size[1])), 16, 2)

                            # Change gamestate of ball
                            if self.ball.getGameState() != BallGameState.ON_ROW and self.ball._lastRowTouched != i:
                                self.ball.changeGameState(BallGameState.ON_ROW)
                                self.ball._lastRowTouched = i
                                #print "Changing ball game state to ON_ROW"

                        rowCollisionFound = True
                        break # break out of for loop if we have a collision

                    #else:
                    #    # If no row collisions were found at all, then we must be in freefall
                    #    #print "\t\tDEBUG no collision! ball geom={} row geom={}".format(row._collGeoms[0], geom)
                    #    if self.ball.getGameState() != BallGameState.FREEFALL:
                    #        self.ball.changeGameState(BallGameState.FREEFALL)
                    #        print "Changing ball game state to FREEFALL"

            if rowCollisionFound:
                # If we found a collision against any row, we can stop testing for any collisions, because we're done. Reset the flag and _exit all for loops_
                rowCollisionFound = False
                break

        #print # blank line

    def updateScore(self):
        # If ball state is FREEFALL at this point, then we can register a score
        if self.scoredFlag:
            self.score += self.GAP_SCORE # GAP_SCORE can increase as the difficulty level increases
            self.scoredFlag = False
            #print "Jyeaw! Score={}".format(self.score)
            self.mm.setMessage("+{}".format(self.GAP_SCORE), [ self.ball._position[0], self.ball._position[1] - self.ball._size[1] ] )


    def preRenderScene(self):
        self.doCollisions()
        self.enforceConstraints()


    def renderScene(self):
        ''' Render scene
            NOTE render() does not 'write' to the screen.
        '''
        self.surface_bg.fill((0,0,0))
        self.game_viewport.fill(self.bg_col)
        
        self.drawGrid(self.game_viewport, self.cell_size, self.game_size)
        self.rm.draw(self.game_viewport, self.cell_size)
        self.ball.draw(self.game_viewport, self.cell_size)


    def displayMessages(self):
        self.mm.draw(self.game_viewport, self.cell_size)

    def displayGameStats(self):

        # Janky hardcoding here... Just trying to meet the game submission deadline
        self.displayMsgScore.changeText("Score: {}".format(self.score))
        textSurfaceScore = self.displayMsgScore.getTextSurface(self.mm._font)
        self.surface_bg.blit(textSurfaceScore, (self.displayMsgScore._position[0] * self.cell_size[0], self.displayMsgScore._position[1] * self.cell_size[1] ))

        self.displayMsgTries.changeText("Tries: {}".format(self.tries))
        textSurfaceTries = self.displayMsgTries.getTextSurface(self.mm._font)
        self.surface_bg.blit(textSurfaceTries, (self.displayMsgTries._position[0] * self.cell_size[0], self.displayMsgTries._position[1] * self.cell_size[1] ))

        if self._gameState == "Crushed":
            textSurfaceCrushed = self.displayMsgCrushed.getTextSurface(self.mm._font)
            self.surface_bg.blit(textSurfaceCrushed, (self.displayMsgCrushed._position[0] * self.cell_size[0], self.displayMsgCrushed._position[1] * self.cell_size[1] ))
            
        if self._gameState == "GameOver":
            textSurfaceGameOver = self.displayMsgGameOver.getTextSurface(self.mm._font)
            self.surface_bg.blit(textSurfaceGameOver, (self.displayMsgGameOver._position[0] * self.cell_size[0], self.displayMsgGameOver._position[1] * self.cell_size[1] ))

    def postRenderScene(self):
        self.updateScore()
        self.displayMessages()
        self.displayGameStats()

        #for i in range(0, ball.getGameState()):
        #    print "BallGameState:{}".format(self.ball.getGameState()),
        #print

        self.surface_bg.blit(self.game_viewport, (0, 0))    # blit the game viewport onto the bigger surface_bg

        pygame.display.flip()


def main():
    # TODO add game states (e.g. intro, playing, menu, etc)
    # TODO add scoring / game logic
    #   Ideas:
    #   Game requires fierce tapping to move (instead of auto move)
    #   Game can include powerups (e.g., auto-move; warp)
    #   Game evaluates difficulty and how "nice" it's been to you; e.g. game knows how many rows are on screen; where you are on screen; when it last gave you a powerup; etc. Judge when to dole out powerups based on that
    #   Scorekeeping requires detecting collisions with a row's gap

    pygame.init()

    game = GameApplication()

    # NOTE timer should be part of application class, too, but this is hack'n'slash.. No time to fix it!!
    prev_time = pygame.time.get_ticks()

    while True:
        curr_time = pygame.time.get_ticks()
        dt_s = (curr_time - prev_time) / 1000.0
        #print "Curr {}, prev {}, dt {}".format(curr_time, prev_time, dt_s)
        prev_time = curr_time

        # ----- Process events
        game.processEvents()

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


if __name__ == '__main__':
    main()
