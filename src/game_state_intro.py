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

import game_state_base
import game_state_main_menu
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

        image_paths = [ "../asset/image/home-made_engine.png" ]
        self.img_surfs = []

        for path in image_paths:
            self.img_surfs.append(pygame.image.load(path))


        self._eventQueue = MessageQueue() # Event queue, e.g. user key/button presses, system events
        self._eventQueue.Initialize(64)

        self._eventQueue.RegisterListener('engine', engineRef, 'Application') # Register the game engine to listen to messages with topic, "Application"

        self.mm = DisplayMessageManager()

        self.splash_screen_threshold = 5 # num of seconds to keep up a splash screen

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
            GameStateImpl.__instance.SetName("Intro State")
        return GameStateImpl.__instance
        
    def EnqueueApplicationQuitMessage(self):
        """Enqueue a message for the application to shut itself down

           NOTES/Observations:
             - This function exists in every game state. That means I can probably consolidate my design to have this function defined in one location, and call it from there.
             - This function could also be more generic; instead of being hardcoded to enqueue a quit message, it could accept input parameters.
        """
        self._eventQueue.Enqueue( { 'topic': 'Application',
                                    'payload': { 'action': 'call_function'
                                               , 'function_name': 'setRunningFlagToFalse'
                                               , 'params' : ''
                                               }
                                  } )

    # TODO Consider changing "pause" to "PushState" or something; doesn't HAVE to be 'pause'
    def Pause(self):
        # TODO check your design - you may need a pointer/reference to the engine here, to be able to push onto the stack.
        #print "GAMESTATE Intro State pausing"
        pass

    # TODO Consider changing "resume" to "PopState" or something; doesn't HAVE to be 'resume'
    def Resume(self):
        # TODO check your design - you may need a pointer/reference to the engine here, to be able to pop from the stack
        #print "GAMESTATE Intro State resume"
        pass

    def ProcessEvents(self, engineRef):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Create a quit request message to the application, to shut itself down. This allows the program to do any necessary cleanup before exiting
                self.EnqueueApplicationQuitMessage()

            # TODO Create a request message to change states, and add it to the Messaging Handler.
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                    # Music # TODO along with the request to change states, make a request to start the music. This redundant, bifurcated logic is crap
                    self.mixer.addMusicFileToMap('Theme', '../asset/audio/falldown_theme.ogg')
                    self.mixer.loadMusicFile('Theme')
                    self.mixer.playMusic()  # Play loaded music file
                                            # TODO add better management of loaded music files; as usual, we're hack'n'slashing
                    engineRef.changeState(game_state_main_menu.GameStateImpl.Instance())

            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:   # Left mouse click
                    # Music # TODO along with the request to change states, make a request to start the music. This redundant, bifurcated logic is crap
                    self.mixer.addMusicFileToMap('Theme', '../asset/audio/falldown_theme.ogg')
                    self.mixer.loadMusicFile('Theme')
                    self.mixer.playMusic()  # Play loaded music file
                                            # TODO add better management of loaded music files; as usual, we're hack'n'slashing
                    engineRef.changeState(game_state_main_menu.GameStateImpl.Instance())

    def ProcessCommands(self, engineRef):
        """Process enqueued messages; translate them into comands to be executed. Then execute them.

           NOTE: This is another function that appears in the same form across multiple gamestates. We possibly could consolidate this into one, as well
        """
        msg = self._eventQueue.Dequeue()
        while msg:
            #print "DEBUG Dequeued message: {}".format(msg)
            topic = msg['topic']
            for listener_obj_dict in self._eventQueue.RegisteredListeners(topic):
                #print "game_state_high_scores: Registered Listener {} processing message {}".format(listener_obj_dict['name'], msg['payload'])

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
        # No updates needed here
        pass

    def PreRenderScene(self, engineRef):
        pass

    def RenderScene(self, engineRef):
        self.surface_bg.fill((255,255,255))
        # TODO add in timer thresholds; cycle through splash screens on keypress, or if no keypress, then after time threshold expires
        posX = int(self.surface_bg.get_width() / 2) - int(self.img_surfs[0].get_width() / 2)
        posY = int(self.surface_bg.get_height() / 2) - int(self.img_surfs[0].get_height() / 2)

        self.surface_bg.blit(self.img_surfs[0], (posX,posY))
        

    def PostRenderScene(self, engineRef):
        pygame.display.flip()

