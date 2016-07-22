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

from display_msg import DisplayMessage
from display_msg_manager import DisplayMessageManager
from message_queue import MessageQueue

import menu_form
import menu_item_label  # TODO figure out the imports necessary to allow importing only menu_form, and getting all the related classes/imports automatically
#import menu_item_spinner


import game_state_base
import game_state_playing
import game_state_intro
import game_state_settings
import game_state_high_scores
import game_state_credits

import sound_and_music
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
		# Snag some vital object refs from the engine object
        self.game_size = engineRef.game_size
        self.screen_size = engineRef.screen_size
        self.cell_size = engineRef.cell_size
        self.surface_bg = engineRef.surface_bg
        self.bg_col = engineRef.bg_col
        self.mixer = engineRef.mixer


        self._eventQueue = MessageQueue() # Event queue, e.g. user key/button presses, system events
        self._eventQueue.Initialize(64)
        self._eventQueue.RegisterListener('engine', engineRef, 'Application') # Register the game engine to listen to messages with topic, "Application"

        self.ui = menu_form.UIForm(engineRef=engineRef) # the LHS engineRef is the function param; the RHS engineRef is the object we're passing in
        self.ui._font = menu_form.UIForm.createFontObject('../asset/font/ARCADE.TTF', 32)   # TODO maybe load one font obj at a higher-level scope than any menu or game state; then pass it in, instead of constructing one at each state change
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([300, 300], self.ui._font, 'Fall Down'), kbSelectIdx=0, action="startFalldown" )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([300, 350], self.ui._font, 'Settings'), kbSelectIdx=1, action="gotoSettings" )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([300, 400], self.ui._font, 'High Scores'), kbSelectIdx=2, action="gotoHighScores" )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([300, 450], self.ui._font, 'Credits'), kbSelectIdx=3, action="gotoCredits" )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([300, 500], self.ui._font, 'Exit'), kbSelectIdx=4, action="exitUI" )

        self.ui._kbSelection = 0 # It is necessary to set the selected item (the keyboard selection) manually. Otherwise, the UI has no way of knowing which item to interact with
        self.ui._maxKbSelection = 4 # Janky hack to know how many kb-interactive items are on the form # TODO is there a better way to specify maximum? Or maybe write an algo that figures this out?


        #Adding another DisplayMessageManager for the Title text. This is a bit hacky..
        self.title_mm = DisplayMessageManager()
        self.title_mm._font = pygame.font.Font('../asset/font/ARCADE.TTF', 64)

        self.titleMsg = DisplayMessage()
        self.titleMsg.create(txtStr='Falldown x64', position=[1,1], color=(192,192,192))


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
            GameStateImpl.__instance.SetName("MainMenu State")
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

    def ProcessEvents(self, engineRef):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Create a quit request message to the application, to shut itself down. This allows the program to do any necessary cleanup before exiting
                self.EnqueueApplicationQuitMessage()

            if event.type == pygame.KEYDOWN:
                action = self.ui.processKeyboardEvent(event, engineRef)

                # TODO perhaps put this logic into ProcessCommands, so it can be triggered via keyboard, mouse, joystick, whatever
                if action == 'startFalldown':
                    self.mixer.stopMusic()
                    engineRef.changeState(game_state_playing.GameStateImpl.Instance())
                elif action == 'gotoSettings':
                    engineRef.changeState(game_state_settings.GameStateImpl.Instance())
                elif action == 'gotoHighScores':
                    engineRef.changeState(game_state_high_scores.GameStateImpl.Instance())
                elif action == 'gotoCredits':
                    engineRef.changeState(game_state_credits.GameStateImpl.Instance())
                elif action == 'exitUI':
                    # Create a quit request message to the application, to shut itself down. This allows the program to do any necessary cleanup before exiting
                    self.EnqueueApplicationQuitMessage()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                action = self.ui.processMouseEvent(event, engineRef)

                # TODO perhaps put this logic into ProcessCommands, so it can be triggered via keyboard, mouse, joystick, whatever
                if action == 'startFalldown':
                    engineRef.changeState(game_state_playing.GameStateImpl.Instance())
                elif action == 'gotoSettings':
                    engineRef.changeState(game_state_settings.GameStateImpl.Instance())
                elif action == 'gotoHighScores':
                    engineRef.changeState(game_state_high_scores.GameStateImpl.Instance())
                elif action == 'gotoCredits':
                    engineRef.changeState(game_state_credits.GameStateImpl.Instance())
                elif action == 'exitUI':
                    engineRef.isRunning = False

            elif event.type == sound_and_music.SoundNMusicMixer.SONG_END_EVENT:
                self.mixer.loadMusicFile('Theme')
                self.mixer.playMusic()  # No matter what song was playing, load up the theme song next and play it
                                        # TODO add config options for music on/off; obey those settings.

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

                    if objRef is engineRef:
                        fn_ptr(argsDict)    # If the object is the engine, we don't need to pass the engineRef to it. i.e., the obj will already have its own self reference. TODO make this logic standard across all game states?
                        # NOTE: Slight cheat here: because this menu is its own event listener, and it's the only one, we pass in engineRef (the application object reference), instead of passing self (as we do in other game states). fn_ptr already points to self.DoUICommand. Admittedly, this is probably over-complicated, but it works..
                    else:
                        fn_ptr(engineRef, argsDict)

            msg = self._eventQueue.Dequeue()


    def Update(self, engineRef, dt_s, cell_size):
        self.ui.update(dt_s)

    def PreRenderScene(self, engineRef):
        pass

    def RenderScene(self, engineRef):
        self.surface_bg.fill((0,0,0))

        self.ui.render(self.surface_bg)

        textSurf = self.titleMsg.getTextSurface(self.title_mm._font)
        self.surface_bg.blit(textSurf, (self.titleMsg._position[0] * self.cell_size[0], self.titleMsg._position[1] * self.cell_size[1]))
        

    def PostRenderScene(self, engineRef):
        # Draw a box around the selected menu item
        # NOTE: I could've put the box in the renderScene function, but the box is technically an "overlay". Also, whatever, who cares? :-D

        ## # TODO perhaps make a function in the menuform class that draws the selection (and make it customizable?)

        # Flip the buffers
        pygame.display.flip()



