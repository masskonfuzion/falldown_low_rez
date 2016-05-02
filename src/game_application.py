# Import game objects (perhaps this can go into a "game manager" of some sort?)
from ball import Ball
from row import Row
from row_manager import RowManager
from ball_game_state import BallGameState
from display_msg import DisplayMessage
from display_msg_manager import DisplayMessageManager
from message_queue import MessageQueue
import pygame
import sys

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
        self._states = []   # States are managed via stack, which we will implement using a Python list

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

        self._eventQueue = MessageQueue() # Event queue, e.g. user key/button presses, system events
        self._eventQueue.Initialize(64)

        #self._cmdQueue = MessageQueue() # Command queue, e.g. "Start moving left"
        #self._cmdQueue.Initialize(64)

        # Register Event Listeners
        self._eventQueue.RegisterListener('ball', self.ball, 'PlayerControl')

        # Register Command Listeners
        #self._cmdQueue.RegisterListener('ball', self.ball, 'PlayerControl')

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

    def cleanup(self):
        pass

    def drawGrid(self, screen, cell_size, screen_size):
        for i in range(0, 63):
            color = 192, 192, 192
            pygame.draw.line(screen, color, ( (i + 1) * cell_size[0], 0                      ), ( (i + 1) * cell_size[1], screen_size[1]         ) )
            pygame.draw.line(screen, color, ( 0                     , (i + 1) * cell_size[0] ), ( screen_size[1]        , (i + 1) * cell_size[1] ) )


    def changeState(self, toState):
        """Change State to toState"""
        fromState = self.PopState() # Get the current state and then pop it off the stack
        if fromState:
            fromState.Cleanup()

        self.PushState(toState)
        self.GetState().Init()

    def pushState(self, toState):
        """Push toState onto the stack"""
        self._states.append(toState)

    def popState(self):
        """Remove state from the stack, and return it"""
        fromState = None
        if self._states:
            fromState = self._states.pop()
        return fromState

    def update(self, dt_s, cell_size):
        """Call Update() on state at top of stack
           
           Call State's Update(), passing in a reference to the engine. The state may need a reference to the engine, especially when the engine has valuable data, e.g. time keeping or other objects the state needs access to
        """
        #self.GetState().Update(self)

        # HORRENDOUS state mgmt style here. Use State Pattern instead
		# TODO move this stuff into the playing state
        if self._gameState == "Playing":
            self.ball.update(dt_s, cell_size)
            self.rm.update(dt_s, cell_size)
            self.mm.update(dt_s, cell_size)

            self.updateDifficulty()

    def processEvents(self):
        """Call ProcessEvents on state at top of stack"""
        #self.GetState().ProcessEvents(self)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # TODO Create a quit request message, and add it to the Messaging Handler. Oh yeah, also make a Messaging Handler
                sys.exit()

            # TERRIBLE state mgmt style here
            if self._gameState == "Playing":
                if event.type == pygame.KEYDOWN:
                    # Left arrow key
                    if (event.key == pygame.K_LEFT or event.key == pygame.K_j):
                        #self.ball.controlState.setLeftKeyPressedTrue()
                        # NOTE: Every message must have an 'action' key/val. The message parser will look for the 'action' in order to know what to do
                        self._eventQueue.Enqueue( { 'topic': 'PlayerControl',
                                                    'payload': { 'action': 'call_function'
                                                               , 'function_name': 'setLeftKeyPressedTrue'
                                                               , 'params' : ''
                                                               }
                                                  } ) # here, the call keyword says that the message payload is an instruction to call a function
                        # TODO Maybe make the params a string of key=value pairs - split on '='
                    # Right arrow key
                    elif (event.key == pygame.K_RIGHT or event.key == pygame.K_l):
                        #self.ball.controlState.setRightKeyPressedTrue()
                        self._eventQueue.Enqueue( { 'topic': 'PlayerControl', 
                                                    'payload': { 'action': 'call_function'
                                                               , 'function_name': 'setRightKeyPressedTrue'
                                                               , 'params': ''
                                                               }
                                                  }) # here, the call keyword says that the message payload is an instruction to call a function
                elif event.type == pygame.KEYUP:
                    if (event.key == pygame.K_LEFT or event.key == pygame.K_j):
                        #self.ball.controlState.setLeftKeyPressedFalse()
                        self._eventQueue.Enqueue( { 'topic': 'PlayerControl', 
                                                    'payload': { 'action': 'call_function'
                                                               , 'function_name': 'setLeftKeyPressedFalse'
                                                               , 'params': ''
                                                               }
                                                  } ) # here, the call keyword says that the message payload is an instruction to call a function
                    elif (event.key == pygame.K_RIGHT or event.key == pygame.K_l):
                        #self.ball.controlState.setRightKeyPressedFalse()
                        self._eventQueue.Enqueue( { 'topic': 'PlayerControl',
                                                    'payload': { 'action': 'call_function'
                                                               , 'function_name': 'setRightKeyPressedFalse'
                                                               , 'params': ''
                                                               }
                                                  }) # here, the call keyword says that the message payload is an instruction to call a function

			# TODO make these other states into GameState instances
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

    def processCommands(self):
        """Call ProcessEvents on state at top of stack"""
        #self.GetState().ProcessCommands(self)

        msg = self._eventQueue.Dequeue()
        while msg:
            #print "DEBUG Dequeued message: {}".format(msg)
            topic = msg['topic']
            for listener_obj_dict in self._eventQueue.RegisteredListeners(topic):
                #print "DEBUG Registered Listener {} processing message {}".format(listener_obj_dict['name'], msg['payload'])

                # Evaluate the 'action' key to know what to do. The action dictates what other information is required to be in the message
                if msg['payload']['action'] == 'call_function':
                    # The registered listener had better have the function call available heh... otherwise, kaboom
                    objRef = listener_obj_dict['ref']
                    fn_ptr = getattr(objRef.controlState, msg['payload']['function_name']) # TODO un-hardcode the ball's "controlState" attr -- make it possible to customize which obj attribute is responsible for handling the command
                    #args = msg['params'].split('=') # NOTE the params should be a comma-separated list of = separated key/vals, e.g. params = "a=1,b=2,c=3,..."

                    #eval(fn_ptr)
                    fn_ptr()

            msg = self._eventQueue.Dequeue()


    def enforceConstraints(self):
        # (e.g. constrain ball to screen space)
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
        """Call PreRender on state at top of stack"""
        #self.GetState().PreRenderScene(self)

        self.doCollisions()
        self.enforceConstraints()


    def renderScene(self):
        ''' Render scene
            NOTE render() does not 'write' to the screen.
        '''
        """Call PreRender on state at top of stack"""
        #self.GetState().RenderScene(self)

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
        """Call PreRender on state at top of stack"""
        #self.GetState().PostRenderScene(self)

        self.updateScore()
        self.displayMessages()
        self.displayGameStats()

        #for i in range(0, ball.getGameState()):
        #    print "BallGameState:{}".format(self.ball.getGameState()),
        #print

        self.surface_bg.blit(self.game_viewport, (0, 0))    # blit the game viewport onto the bigger surface_bg

        pygame.display.flip()

