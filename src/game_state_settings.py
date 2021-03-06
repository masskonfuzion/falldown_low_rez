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
import game_state_main_menu

import menu_item_base
import menu_item_spinner
import menu_item_label
import menu_form

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
        #print "{} state Init()".format(self._name)

		# Snag some vital object refs from the engine object
        self.game_size = engineRef.game_size
        self.screen_size = engineRef.screen_size
        self.cell_size = engineRef.cell_size
        self.surface_bg = engineRef.surface_bg
        self.bg_col = engineRef.bg_col
        self.mixer = engineRef.mixer


        self._eventQueue = MessageQueue() # Event queue, e.g. user key/button presses, system events
        self._eventQueue.Initialize(16)

        # NOTE could optimize images by loading UI graphics at a higher level than this, e.g. to make available to all menus: main menu, settings, in-game pause, etc.
        self.uiImgCache = { 'spinner':{ 'left' : menu_item_base.MenuItemBase.createImage(os.path.normpath(engineRef.exepath + "/../asset/image/back.png"))
                                      , 'right': menu_item_base.MenuItemBase.createImage(os.path.normpath(engineRef.exepath + "/../asset/image/forward.png"))
                                      }
                          }

        self.ui = menu_form.UIForm( os.path.normpath(engineRef.exepath + '/../data/config/settings.json'), engineRef=engineRef ) # I hope the program understands that the engineRef on the left is the function parameter, and the one on the right is the passed-in reference
        self.ui._font = menu_form.UIForm.createFontObject( os.path.normpath(engineRef.exepath + '/../asset/font/ARCADE.TTF'), 32 )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([50,80], self.ui._font, 'Number of Tries'), kbSelectIdx=None )
        self.ui.addMenuItem( menu_item_spinner.MenuItemSpinner(self.ui._boundObj, 'numTries', [50,120], self.ui._font, self.uiImgCache['spinner']['left'], self.uiImgCache['spinner']['right'], range(1, 5+1)), kbSelectIdx=0 )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([50,180], self.ui._font, 'Row Spacing') )
        self.ui.addMenuItem( menu_item_spinner.MenuItemSpinner(self.ui._boundObj, 'difficulty.initialRowSpacing', [50,220], self.ui._font, self.uiImgCache['spinner']['left'], self.uiImgCache['spinner']['right'], range(3,6+1)), kbSelectIdx=1 )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([50,280], self.ui._font, 'Screen Row Travel Time (seconds)') )
        self.ui.addMenuItem( menu_item_spinner.MenuItemSpinner(self.ui._boundObj, 'difficulty.initialRowScreenClearTime', [50,320], self.ui._font, self.uiImgCache['spinner']['left'], self.uiImgCache['spinner']['right'], range(6, 10+1)), kbSelectIdx=2 )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([50,380], self.ui._font, 'Music Volume') )
        self.ui.addMenuItem( menu_item_spinner.MenuItemSpinner(self.ui._boundObj, 'mixer.musicVol', [50,420], self.ui._font, self.uiImgCache['spinner']['left'], self.uiImgCache['spinner']['right'], range(0, 10+1)), kbSelectIdx=3, action='setMusicVol' )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([50,480], self.ui._font, 'SFX Volume') )
        self.ui.addMenuItem( menu_item_spinner.MenuItemSpinner(self.ui._boundObj, 'mixer.sfxVol', [50,520], self.ui._font, self.uiImgCache['spinner']['left'], self.uiImgCache['spinner']['right'], range(0, 10+1)), kbSelectIdx=4, action='setSfxVol' )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([50,600], self.ui._font, 'Return'), kbSelectIdx=5, action="exitUI" )
        self.ui.synchronize(0, 5)

        # TODO possibly make the menu require the user to navigate to items, and then press "enter" or something to activate the selected item for editing?

        #Adding another DisplayMessageManager for the Title text. This is a bit hacky..
        self.title_mm = DisplayMessageManager()
        self.title_mm._font = pygame.font.Font( os.path.normpath(engineRef.exepath + '/../asset/font/ARCADE.TTF'), 64 )

        self.titleMsg = DisplayMessage()
        self.titleMsg.create(txtStr='Settings', position=[1,1], color=(192,192,192))

        # Register Event Listeners
        self._eventQueue.RegisterListener('self', self, 'UIControl')    # Register "myself" as an event listener
        self._eventQueue.RegisterListener('engine', engineRef, 'Application') # Register the game engine to listen to messages with topic, "Application"

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
            GameStateImpl.__instance.SetName("Settings State")
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
                self.ui.saveConfigToFile()
                engineRef.changeState(game_state_main_menu.GameStateImpl.Instance())
            elif argsDict['uiCommand'] == 'setMusicVol':
                self.mixer.setMusicVolume(self.ui._boundObj['mixer.musicVol'] / 10.0)
            elif argsDict['uiCommand'] == 'setSfxVol':
                self.mixer.setSfxVolume(self.ui._boundObj['mixer.sfxVol'] / 10.0)
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
                # Note: processKeyboardEvent causes things to happen in the menu_form scope (e.g. increment/decrement values, etc).
                # The action variable contains further info/instructions to process in this scope
                action = self.ui.processKeyboardEvent(event, engineRef)
                if action:
                    self.EnqueueUICommandMessage(action)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                action = self.ui.processMouseEvent(event, engineRef)
                if action:
                    self.EnqueueUICommandMessage(action)

            elif event.type == pygame.MOUSEBUTTONUP:
                action = self.ui.processMouseEvent(event, engineRef)

            elif event.type == sound_and_music.SoundNMusicMixer.SONG_END_EVENT:
                # Music # TODO along with the request to change states, make a request to start the music. This redundant, bifurcated logic is crap
                self.mixer.addMusicFileToMap('Theme', os.path.normpath(engineRef.exepath + '/../asset/audio/falldown_theme.ogg'))
                self.mixer.loadMusicFile('Theme')
                self.mixer.playMusic()  # Play loaded music file

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
        self.surface_bg.fill((0,0,0))

        # Render the title text surface
        textSurf = self.titleMsg.getTextSurface(self.title_mm._font)
        self.surface_bg.blit(textSurf, (self.titleMsg._position[0] * self.cell_size[0], self.titleMsg._position[1] * self.cell_size[1]))

        # Render the UI
        self.ui.render(self.surface_bg)

    def PostRenderScene(self, engineRef):
        # TODO Draw a box around the selected menu item
        # Flip the buffers
        pygame.display.flip()

