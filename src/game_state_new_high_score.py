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

from display_msg import DisplayMessage
from display_msg_manager import DisplayMessageManager
from message_queue import MessageQueue

import game_state_base
import game_state_high_scores

import menu_item_base
import menu_item_spinner
import menu_item_label
import menu_item_textbox
import menu_form

import sound_and_music

import json

# NOTE: Looks like we have to use full import names, because we have circular imports (i.e. intro state imports playing state; but playing state imports intro state. Without using full import names, we run into namespace collisions and weird stuff)

class GameStateImpl(game_state_base.GameStateBase):
    __instance = None

    def __new__(cls):
        """Override the instantiation of this class. We're creating a singleton yeah"""
        return None

    def __init__(self):
        """ This shouldn't run.. We call __init__ on the __instance member"""
        pass

    def Init(self, engineRef, takeWith=None):
        """Initialize state

           takeWith is an obj that was passed in by the state that transitioned into this state. It should be a mutable object (i.e. a list or dict)
        """
        #print "{} state Init()".format(self._name)

		# Snag some vital object refs from the engine object
        self.game_size = engineRef.game_size
        self.screen_size = engineRef.screen_size
        self.cell_size = engineRef.cell_size
        self.surface_bg = engineRef.surface_bg
        self.bg_col = engineRef.bg_col
        self.shared_ref = takeWith                      # TODO Maybe name this better. This is the object passed in by the last state that transitioned to this state
        self.mixer = engineRef.mixer

        self.surface_overlay = pygame.Surface((640, 480))

        self.blit_center = ( self.surface_bg.get_size()[0] / 2 - self.surface_overlay.get_size()[0] / 2, self.surface_bg.get_size()[1] / 2 - self.surface_overlay.get_size()[1] / 2 )

        self._eventQueue = MessageQueue() # Event queue, e.g. user key/button presses, system events
        self._eventQueue.Initialize(16)

        self.displayMsgScore = DisplayMessage()
        self.displayMsgScore.create(txtStr="New High!!", position=[66, 5], color=(192,192,192))

        # TODO Allow customization of text colors in the UI
        self.ui = menu_form.UIForm(engineRef=engineRef) # the LHS engineRef is the function param; the RHS engineRef is the object we're passing in
        self.ui._font = menu_form.UIForm.createFontObject( os.path.normpath(engineRef.exepath + '/../asset/font/ARCADE.TTF'), 32 )   # TODO maybe load one font obj at a higher-level scope than any menu or game state; then pass it in, instead of constructing one at each state change
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([200, 200], self.ui._font, 'New High Score!'), kbSelectIdx=None )
        self.ui.addMenuItem( menu_item_textbox.MenuItemTextbox( self.shared_ref, 'name', [200, 250], self.ui._font, locked=False), kbSelectIdx=0 )
        self.ui.addMenuItem( menu_item_textbox.MenuItemTextbox( self.shared_ref, 'score', [200, 300], self.ui._font, locked=True), kbSelectIdx=None, action=None )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([200, 350], self.ui._font, 'View High Scores'), kbSelectIdx=1, action="exitUI" )
        self.ui.synchronize(0, 1)

        # Register Event Listeners
        self._eventQueue.RegisterListener('self', self, 'UIControl')    # Register "myself" as an event listener
        self._eventQueue.RegisterListener('engine', engineRef, 'Application') # Register the game engine to listen to messages with topic, "Application"


        self._highScoresFilePath = os.path.normpath(engineRef.exepath + '/../data/scores/highscores.json')
        # TODO move high score loading into a function
        with open(self._highScoresFilePath, 'r') as fd:
            self._highScores = json.load(fd)
            #print "game_state_new_high_score: loaded high scores: {}".format(self._highScores)


    def Cleanup(self):
        # NOTE this class is a port from a C++ class. Because Python is garbage-collected, Cleanup() is probably not necessary here. But it's included for completeness
        pass

    @staticmethod
    def Instance():
        """Return the instance reference. Create it if it doesn't exist
           
           This method is a static method because it does not use any object
        """
        if GameStateImpl.__instance is None:
            GameStateImpl.__instance = super(GameStateImpl, GameStateImpl).__new__(GameStateImpl)
            GameStateImpl.__instance.__init__()
            GameStateImpl.__instance.SetName("New High Score State")
        return GameStateImpl.__instance
        

    # TODO Consider changing "pause" to "PushState" or something; doesn't HAVE to be 'pause'
    def Pause(self):
        pass

    # TODO Consider changing "resume" to "PopState" or something; doesn't HAVE to be 'resume'
    def Resume(self):
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

    def EnqueueUICommandMessage(self, action):
        """Enqueue a UI command message for handling

           # NOTE: Every message must have an 'action' key/val. The message parser will look for the 'action' in order to know what to do
        """
        self._eventQueue.Enqueue( { 'topic': 'UIControl',
                                    'payload': { 'action': 'call_function'
                                               , 'function_name': 'DoUICommand'
                                               , 'params' : 'uiCommand="{}"'.format(action)
                                               }
                                  } ) # here, the call keyword says that the message payload is an instruction to call a function

    def DoUICommand(self, engineRef, argsDict):
        """
           NOTE: This function assumes argsDict has one key only: uiCommand. The value of that key dictates what to do
        """
        try:
            if argsDict['uiCommand'] == 'exitUI':
                # TODO put highscores file rewrite into a function
                for rank in range( 9, int(self.shared_ref['rank']), -1):   # TODO un-hardcode the max of 9 if you intend to keep more than 10 high scores (currenly 0-index, from 0 - 9)
                    self._highScores[str(rank)] = self._highScores[str(rank - 1)]
                self._highScores[self.shared_ref['rank']] = { 'score': self.shared_ref['score'], 'name': self.shared_ref['name'] }
                #print "Going to write new highscores file: {}".format(self._highScores)
                with open(self._highScoresFilePath, 'w') as fd:
                    json.dump(self._highScores, fd)

                engineRef.changeState( game_state_high_scores.GameStateImpl.Instance() )
        except KeyError as e:
            # if there is no uiCommand defined, don't do anything
            # (could have also tested if argsDict['uiCommand'] exists, without exception handling, but I like the way the code looks here)
            pass

    def ProcessEvents(self, engineRef):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Create a quit request message to the application, to shut itself down. This allows the program to do any necessary cleanup before exiting
                self.EnqueueApplicationQuitMessage()

            if event.type == pygame.KEYDOWN:
                #print "game_state_new_high_score: KEYDOWN event: {}".format(event)
                # TODO Perhaps add to the UI a way to determine what the "action activator buttons" should be. e.g., some menus should respond to ESC key, others only ENTER, SPACE, etc. The pause menu should respond to "p"
                action = self.ui.processKeyboardEvent(event, engineRef)
                if action:
                    self.EnqueueUICommandMessage(action)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                #print "game_state_new_high_score: MOUSEBUTTONDOWN event: {}".format(event)
                action = self.ui.processMouseEvent(event, engineRef)
                if action:
                    self.EnqueueUICommandMessage(action)

            elif event.type == sound_and_music.SoundNMusicMixer.SONG_END_EVENT:
                self.mixer.loadMusicFile('Theme')
                self.mixer.playMusic()  # No matter what song was playing, load up the theme song next and play it

    def ProcessCommands(self, engineRef):
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
                    argsDict = eval("dict({})".format(msg['payload']['params']))

                    # NOTE: Slight cheat here: because this menu is its own event listener, and it's the only one, we pass in engineRef (the application object reference), instead of passing self (as we do in other game states). fn_ptr already points to self.DoUICommand. Admittedly, this is probably over-complicated, but it works..
                    if objRef is engineRef:
                        fn_ptr(argsDict)    # If the object is the engine, we don't need to pass the engineRef to it. i.e., the obj will already have its own self reference.
                        # NOTE: Slight cheat here: because this menu is its own event listener, and it's the only one, we pass in engineRef (the application object reference), instead of passing self (as we do in other game states). fn_ptr already points to self.DoUICommand. Admittedly, this is probably over-complicated, but it works..
                    else:
                        fn_ptr(engineRef, argsDict)

            msg = self._eventQueue.Dequeue()

    def Update(self, engineRef, dt_s, cell_size):
        self.ui.update(dt_s)

    def PreRenderScene(self, engineRef):
        pass

    def RenderScene(self, engineRef):
        self.surface_bg.fill((0,0,0))          # I think we want to NOT fill, so we can overlay.
        
        # Render the UI
        self.ui.render(self.surface_bg)

    def PostRenderScene(self, engineRef):
        pygame.display.flip()



