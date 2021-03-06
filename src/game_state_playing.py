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

# Import game objects (perhaps this can go into a "game manager" of some sort?)
import pygame
import sys
import os

from ball import Ball
from row import Row
from row_manager import RowManager
from ball_game_state import BallGameState
from display_msg import DisplayMessage
from display_msg_manager import DisplayMessageManager
from message_queue import MessageQueue

import game_state_base
import game_state_pause
import game_state_main_menu
import game_state_new_high_score

import sound_and_music

import dot_access_dict
import json
import collections

# NOTE: Looks like we have to use full import names, because we have circular imports (i.e. intro state imports playing state; but playing state imports intro state. Without using full import names, we run into namespace collisions and weird stuff)

class GameplayStats(object):
    def __init__(self, configDict, highScoresDict):
        self.scoredFlag = False # Flag that tells whether player has scored or not
        self.score = 0
        self.GAP_SCORE = 10  # NOTE Scoring elements could be managed by a class/object. But whatever, no time!
        self.tries = configDict['numTries']   # We're calling them "tries" because "lives" doesn't make sense for a ball :-D
        self._gotCrushed = False
        self._gameState = "Playing"
        self.level = 1
        self._lastDifficultyIncreaseScore = 0

        # 64 is hardcoded here because the Low Rez Jam rules required a 64x64 grid. The update delay is calculated in terms of amt of time needed for a Falldown row to clear 64 grid rows
        self.initialRowUpdateDelay = float(configDict['difficulty.initialRowScreenClearTime']) / float(64) 
        self.initialRowSpacing = configDict['difficulty.initialRowSpacing']
        self.achievedHighScore = False
        self._newHighScore = None
        self.highScores = highScoresDict


class GameStateImpl(game_state_base.GameStateBase):
    __instance = None

    def __new__(cls):
        """Override the instantiation of this class. We're creating a singleton yeah"""
        return None

    def __init__(self):
        """ This shouldn't run.. We call __init__ on the __instance member"""
        #super(GameStateImpl, self).__init__()
        #self.SetName("Playing State")
        #print "GAMESTATE Playing State __init__ running (creating data members and method functions)"
        pass

    def Init(self, engineRef, takeWith=None):
		# Snag some vital object refs from the engine object
        self.game_size = engineRef.game_size
        self.screen_size = engineRef.screen_size
        self.cell_size = engineRef.cell_size
        self.surface_bg = engineRef.surface_bg
        self.game_viewport = engineRef.game_viewport
        self.bg_col = engineRef.bg_col
        self.mixer = engineRef.mixer

        # TODO perhaps move the loading of this config to the main game engine. Then, simply pass a reference to the config object into this function, rather than doing the loading here
        # Load config file
        with open(os.path.normpath(engineRef.exepath + '/../data/config/settings.json'), 'r+') as fd:
            cfgFromFile = json.load(fd)
        config = dot_access_dict.DotAccessDict(cfgFromFile)

        with open(os.path.normpath(engineRef.exepath + '/../data/scores/highscores.json'), 'r') as fd:
            highScores = json.load(fd)

        self.vital_stats = GameplayStats(config, highScores)
        # TODO - Fix Gameplaystats. Right now, it's a patchwork object that takes some items that were loaded in from a cfg file, but others that are hard-coded. The patchwork is an artifact of the patchwork design/implementation of this game (I'm adding things as I figure out how to, heh)

        self.ball = Ball()
        self.ball._accumulator_s[1] = 0.0
        self.ball.setPosition(32, 0) # Position is given in coordinates on the 64x64 grid. Actual screen coordinates are calculated from grid coordinates
        self.ball.setSpeed(0,1)
        self.ball.setMaxSpeed(1,1)
        self.ball.changeGameState(BallGameState.FREEFALL)
        #print "Changing ball game state to FREEFALL"

        self._eventQueue = MessageQueue() # Event queue, e.g. user key/button presses, system events
        self._eventQueue.Initialize(64)

        self.mm = DisplayMessageManager()

        self.rm = RowManager()
        self.rm.initLevel(self.vital_stats.initialRowSpacing, self.vital_stats.initialRowUpdateDelay, self.cell_size) 

        self.displayMsgScore = DisplayMessage()
        self.displayMsgScore.create(txtStr="Score: ", position=[66, 5], color=(192,192,192))

        self.displayMsgTries = DisplayMessage()
        self.displayMsgTries.create(txtStr="Tries: ", position=[66, 10], color=(192,192,192))
    
        self.displayMsgLevel = DisplayMessage()
        self.displayMsgLevel.create(txtStr="Level: ", position=[66, 20], color=(192,192,192))

        self.displayMsgCrushed = DisplayMessage()
        self.displayMsgCrushed.create(txtStr="Crushed :-(", position=[66, 30], color=(192,192,192))
    
        self.displayMsgGameOver = DisplayMessage()
        self.displayMsgGameOver.create(txtStr="GameOver :-(", position=[66, 32], color=(192,192,192))

        # Register Event Listeners
        self._eventQueue.RegisterListener('ball', self.ball.controlState, 'PlayerControl')
        self._eventQueue.RegisterListener('rowmgr', self.rm, 'Difficulty')
        self._eventQueue.RegisterListener('mixer', self.mixer, 'PlaySfx')
        self._eventQueue.RegisterListener('engine', engineRef, 'Application') # Register the game engine to listen to messages with topic, "Application"

        # Initialize sound effects
        # TODO make a class or some other smarter way to manage loading the sound effects
        self.mixer.addSfxFileToMap('gap'        , os.path.normpath(engineRef.exepath + '/../asset/audio/gap.wav'))
        self.mixer.addSfxFileToMap('crushed'    , os.path.normpath(engineRef.exepath + '/../asset/audio/explosion2.wav'))
        self.mixer.addSfxFileToMap('levelUp'    , os.path.normpath(engineRef.exepath + '/../asset/audio/powerup2.wav'))
        self.mixer.loadSfxFiles()
        self.mixer.setSfxVolume(config['mixer.sfxVol'] / 10.0)  # TODO Design a way to avoid hard-coding the config keys here
        # A note on dependencies: setSfxVolume has to come after sound effects are loaded. That is because Pygame sets sfx levels per Sound object; the sounds must be loaded to set their volume
        # Music volume, on the other hand, appears to be configurable at any time

        # Add music files to mapping
        # NOTE: We could have initialized the playing state music files in the main menu (along with the main menu music), because the mixer object is shared across all gamestates. But, we're initializing them here because they logically belong to this gamestate
        self.mixer.addMusicFileToMap('level'    , os.path.normpath(engineRef.exepath + '/../asset/audio/gameplay_music_01.ogg'))
        self.mixer.addMusicFileToMap('gameOver' , os.path.normpath(engineRef.exepath + '/../asset/audio/gameover.ogg'))
        self.mixer.setMusicVolume(config['mixer.musicVol'] / 10.0)  # TODO Design a way to avoid hard-coding the config keys here

        self.mixer.loadMusicFile('level')
        self.mixer.playMusic(repeatMode=sound_and_music.SoundNMusicMixer.REPEAT_TRACK)   # TODO revisit music playback. Maybe make a few songs to randomly shuffle?


    def Cleanup(self):
        # NOTE this class is a port from a C++ class. Because Python is garbage-collected, Cleanup() is probably not necessary here. But it's included for completeness
        #print "GAMESTATE Playing State cleaning up."
        pass

    @staticmethod
    def Instance():
        """Return the instance reference. Create it if it doesn't exist
           
           This method is a static method because it does not use any object
        """
        if GameStateImpl.__instance is None:
            GameStateImpl.__instance = super(GameStateImpl, GameStateImpl).__new__(GameStateImpl)
            GameStateImpl.__instance.__init__()
            GameStateImpl.__instance.SetName("Playing State")
            #print "GAMESTATE Playing State creating __instance object {}".format(GameStateImpl.__instance)

        #print "GAMESTATE Playing State getting __instance {}".format(GameStateImpl.__instance)
        return GameStateImpl.__instance
        

    # TODO Consider changing "pause" to "PushState" or something; doesn't HAVE to be 'pause'
    def Pause(self):
        # TODO check your design - you may need a pointer/reference to the engine here, to be able to push onto the stack.
        #print "GAMESTATE Playing State pausing"
        pass

    # TODO Consider changing "resume" to "PopState" or something; doesn't HAVE to be 'resume'
    def Resume(self):
        # TODO check your design - you may need a pointer/reference to the engine here, to be able to pop from the stack
        #print "GAMESTATE Playing State resume"
        pass

    def EnqueueApplicationQuitMessage(self):
        """Enqueue a message for the application to shut itself down
        """
        self._eventQueue.Enqueue( { 'topic': 'Application',
                                    'payload': { 'action': 'call_function'
                                               , 'function_name': 'setRunningFlagToFalse'
                                               , 'params' : ''
                                               }
                                  } )

    def ProcessEvents(self, engineRef):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Create a quit request message to the application, to shut itself down. This allows the program to do any necessary cleanup before exiting
                self.EnqueueApplicationQuitMessage()

            # Basic state mgmt style here
            if self.vital_stats._gameState == "Playing":
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
                    # Right arrow key
                    elif (event.key == pygame.K_RIGHT or event.key == pygame.K_l):
                    #self.ball.controlState.setRightKeyPressedTrue()
                        self._eventQueue.Enqueue( { 'topic': 'PlayerControl', 
                                                    'payload': { 'action': 'call_function'
                                                               , 'function_name': 'setRightKeyPressedTrue'
                                                               , 'params': ''
                                                               }
                                                  }) # here, the call keyword says that the message payload is an instruction to call a function
                    elif (event.key == pygame.K_p):
                        engineRef.pushState(game_state_pause.GameStateImpl.Instance())

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

            elif self.vital_stats._gameState == "Crushed":
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RETURN:

                        if self.vital_stats.tries > 0:
                            self.vital_stats._gameState = "Playing"
                        else:
                            self.vital_stats._gameState = "GameOver"
                            # TODO move high score check into a function
                            # Note that for large dicts, keys() is sloowwww.. But here, we only have 10 high scores
                            for rank in sorted(self.vital_stats.highScores.keys()):
                                if self.vital_stats.score > self.vital_stats.highScores[rank]['score']:
                                    self.vital_stats.achievedHighScore = True
                                    self.vital_stats._newHighScore = { 'rank': rank, 'score': self.vital_stats.score, 'name':'AAA' }  # create the new high score obj as part of vital_stats, so it belongs to a scope outside this function (to make doubly sure it still exists when this function exits (though it shouldn't matter, because all Python objs are created on the heap, no?))
                                    break

                            # NOTE: Here, we are not enqueuing the play music function call as a message because the Pygame music mixer is already asynchronous. We can simply call playMusic(), and Pygame handles the rest
                            self.mixer.loadMusicFile('gameOver')
                            self.mixer.playMusic()

                        self.vital_stats._gotCrushed = False

                        # Super janky way of resetting the ball. Running out of time
                        self.ball._accumulator_s[1] = 0.0
                        self.ball.setPosition(32, 0) # Position is given in coordinates on the 64x64 grid. Actual screen coordinates are calculated from grid coordinates
                        self.ball.setSpeed(0,1)
                        self.ball.setMaxSpeed(1,1)
                        self.ball.controlState.reset(engineRef)
                        self.ball.changeGameState(BallGameState.FREEFALL)

                        # TODO find a way to reuse the memory space used by the original queue Initialize() call (called during initialization of the Playing State). Right now, we're discarding the old and freshly allocating new space.
                        self._eventQueue.Clear()
                        self._eventQueue.Initialize(64)

                        self.mm.clear()

                        self.rm.initLevel(self.vital_stats.initialRowSpacing, self.vital_stats.initialRowUpdateDelay, self.cell_size) 


            elif self.vital_stats._gameState == "GameOver":
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        #print "PlayingState: GameOver KEYUP"
                        if self.vital_stats.achievedHighScore:
                            #print "You reached a high score!! Better than rank #{}".format(int(self.vital_stats._newHighScore['rank'])+1) # rank is stored as a string repr of an int, zero-based.
                            #print "Passing in newHighScore object {} to changeState()".format(self.vital_stats._newHighScore)

                            # Transition to the state that allows the user to enter a new high score. NOTE We may need to keep that in this data scope, rather than switching to a stand-alone state)
                            engineRef.changeState( game_state_new_high_score.GameStateImpl.Instance(), takeWith=self.vital_stats._newHighScore )
                        else:
                            engineRef.changeState( game_state_main_menu.GameStateImpl.Instance() )

    def ProcessCommands(self, engineRef):
        # TODO maybe put this command extraction logic into a function at the application class level (or base gamestate level). We're reusing the logic in every gamestate instance
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
                    fn_ptr = getattr(objRef, msg['payload']['function_name'])
                    argsDict = eval("dict({})".format(msg['payload']['params']))    # params should be a comma-separated list of key=value pairs, e.g. "a = 5, b = 3"

                    #print "function args: {}".format(argsDict)
                    if argsDict:
                        # In this particular gamestate, we want an argsdict to translate to kwargs. This is because the mixer class is written with kwargs (other classes in other gamestates use dicts, in which case, we pass in argsDict as-is))
                        fn_ptr(self, **argsDict)
                    else:
                        fn_ptr(self)

            msg = self._eventQueue.Dequeue()

    def Update(self, engineRef, dt_s, cell_size):
        # NOTE: How should we Update() and PreRender()? (Acceptable answers also include _not_distinguishing and simply making the PreRender() do what Update() does, and getting rid of Update())
        if self.vital_stats._gameState == "Playing":
            self.ball.update(dt_s, cell_size, self.vital_stats)
            self.rm.update(dt_s, cell_size, self.vital_stats)
            self.mm.update(dt_s, cell_size, self.vital_stats)

            self.updateDifficulty()

    def PreRenderScene(self, engineRef):
        self.doCollisions()
        self.enforceConstraints()

    def RenderScene(self, engineRef):
        self.surface_bg.fill((0,0,0))
        self.game_viewport.fill(self.bg_col)
        
        self.drawGrid(self.game_viewport, self.cell_size, self.game_size)
        self.rm.draw(self.game_viewport, self.cell_size)
        self.ball.draw(self.game_viewport, self.cell_size)


    def drawGrid(self, screen, cell_size, screen_size):
        for i in range(0, 63):
            color = 192, 192, 192
            pygame.draw.line(screen, color, ( (i + 1) * cell_size[0], 0                      ), ( (i + 1) * cell_size[1], screen_size[1]         ) )
            pygame.draw.line(screen, color, ( 0                     , (i + 1) * cell_size[0] ), ( screen_size[1]        , (i + 1) * cell_size[1] ) )

    def PostRenderScene(self, engineRef):
        self.updateScore()
        self.displayMessages()
        self.displayGameStats()

        #for i in range(0, ball.getGameState()):
        #    print "BallGameState:{}".format(self.ball.getGameState()),
        #print

        self.surface_bg.blit(self.game_viewport, (0, 0))    # blit the game viewport onto the bigger surface_bg

        pygame.display.flip()


    def enforceConstraints(self):
        # (e.g. constrain ball to screen space)
        for i in range(0, 2):
            if self.ball._position[i] < 0:
                self.ball._position[i] = 0
                if i == 1 and not self.vital_stats._gotCrushed:
                    self.vital_stats._gotCrushed = True
                    self.vital_stats._gameState = "Crushed"
                    self.vital_stats.tries -= 1

                    self._eventQueue.Enqueue( { 'topic': 'PlaySfx'
                                              , 'payload': { 'action': 'call_function'
                                                           , 'function_name': 'playSfx'
                                                           , 'params': 'nameId="crushed"'
                                                           }
                                              }
                                            )

            if self.ball._position[i] + self.ball._size[i] > 64:
                self.ball._position[i] = 64 - self.ball._size[i]

    
    def updateDifficulty(self):
        # Some hard-coded stuff here -- would like to make a more robust level management system, but I'm scrambling to meet the submission deadline for Low Rez Jam 2016. Maybe I'll update later
        if self.vital_stats.score % 200 == 0 and self.vital_stats._lastDifficultyIncreaseScore < self.vital_stats.score:
            self.vital_stats.level += 1
            self.vital_stats._lastDifficultyIncreaseScore = self.vital_stats.score
            self.mm.setMessage("Level Up!".format(self.vital_stats.GAP_SCORE), [ self.ball._position[0], self.ball._position[1] - self.ball._size[1] ], (192, 64, 64), 8 )
            self._eventQueue.Enqueue( { 'topic': 'Difficulty'
                                      , 'payload': { 'action': 'call_function'
                                                   , 'function_name': 'updateDifficulty'
                                                   , 'params': ''
                                                   }
                                      }
                                    )
            self._eventQueue.Enqueue( { 'topic': 'PlaySfx'
                                      , 'payload': { 'action': 'call_function'
                                                   , 'function_name': 'playSfx'
                                                   , 'params': 'nameId="levelUp"'
                                                   }
                                      }
                                    )


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
                    # NOTE: We need to test for collision with a gap first, then check for the row, because the ball can possibly be in contact with both the row and gap at the same time. That way, the test will indicate when the ball is in contact with the gap but not the row at the same time.
                    if geom.isColliding(self.ball._collGeoms[0], self.cell_size):
                        if geom._type == Row.COLLISION_TYPE_GAP:
                            #print "\t\tDEBUG gap collision! ball geom={} row geom={}".format(row._collGeoms[0], geom)
                            if self.ball.getGameState() != BallGameState.FREEFALL:
                                self.ball.changeGameState(BallGameState.FREEFALL)
                                #print "Changing ball game state to FREEFALL"

                            if self.ball._lastRowScored != i: 
                                self.ball._lastRowScored = i 
                                self.vital_stats.scoredFlag = True # This flag could also be handled as a message from the ball or row or whatever, to the game logic (in a better designed game), to trigger the game logic's score handler
                                self._eventQueue.Enqueue( { 'topic': 'PlaySfx'
                                                          , 'payload': { 'action': 'call_function'
                                                                       , 'function_name': 'playSfx'
                                                                       , 'params': 'nameId="gap"'
                                                                       }
                                                          }
                                                        )

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
                            self.ball._computeCollisionGeometry(self.cell_size) # TODO: the ball should recompute its geometry on a setPosition() call. Perhaps a fn override is needed (right now, setPosition is part of base class)
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

            if rowCollisionFound:
                # If we found a collision against any row, we can stop testing for any collisions, because we're done. Reset the flag and _exit all for loops_
                rowCollisionFound = False
                break

        #print # blank line

    def updateScore(self):
        # If ball state is FREEFALL at this point, then we can register a score
        if self.vital_stats.scoredFlag:
            self.vital_stats.score += self.vital_stats.GAP_SCORE # GAP_SCORE can increase as the difficulty level increases
            self.vital_stats.scoredFlag = False
            #print "Jyeaw! Score={}".format(self.vital_stats.score)
            self.mm.setMessage("+{}".format(self.vital_stats.GAP_SCORE), [ self.ball._position[0], self.ball._position[1] - self.ball._size[1] ] )


    def displayMessages(self):
        self.mm.draw(self.game_viewport, self.cell_size)

    def displayGameStats(self):

        # Janky hardcoding here... Just trying to meet the game submission deadline
        self.displayMsgScore.changeText("Score: {}".format(self.vital_stats.score))
        textSurfaceScore = self.displayMsgScore.getTextSurface(self.mm._font)
        self.surface_bg.blit(textSurfaceScore, (self.displayMsgScore._position[0] * self.cell_size[0], self.displayMsgScore._position[1] * self.cell_size[1] ))

        self.displayMsgTries.changeText("Tries: {}".format(self.vital_stats.tries))
        textSurfaceTries = self.displayMsgTries.getTextSurface(self.mm._font)
        self.surface_bg.blit(textSurfaceTries, (self.displayMsgTries._position[0] * self.cell_size[0], self.displayMsgTries._position[1] * self.cell_size[1] ))

        self.displayMsgLevel.changeText("Level: {}".format(self.vital_stats.level))
        textSurfaceLevel = self.displayMsgLevel.getTextSurface(self.mm._font)
        self.surface_bg.blit(textSurfaceLevel, (self.displayMsgLevel._position[0] * self.cell_size[0], self.displayMsgLevel._position[1] * self.cell_size[1] ))

        if self.vital_stats._gameState == "Crushed":
            textSurfaceCrushed = self.displayMsgCrushed.getTextSurface(self.mm._font)
            self.surface_bg.blit(textSurfaceCrushed, (self.displayMsgCrushed._position[0] * self.cell_size[0], self.displayMsgCrushed._position[1] * self.cell_size[1] ))
            
        if self.vital_stats._gameState == "GameOver":
            textSurfaceGameOver = self.displayMsgGameOver.getTextSurface(self.mm._font)
            self.surface_bg.blit(textSurfaceGameOver, (self.displayMsgGameOver._position[0] * self.cell_size[0], self.displayMsgGameOver._position[1] * self.cell_size[1] ))

