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

import menu_form
import menu_item_label  
#import menu_item_spinner

import game_state_base
import game_state_main_menu
# NOTE: Looks like we have to use full import names, because we have circular imports (i.e. intro state imports playing state; but playing state imports intro state. Without using full import names, we run into namespace collisions and weird stuff)

import sound_and_music

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
        self._eventQueue.Initialize(16)

        self.ui = menu_form.UIForm(engineRef=engineRef) # the LHS engineRef is the function param; the RHS engineRef is the object we're passing in
        self.ui._font = menu_form.UIForm.createFontObject( os.path.normpath(engineRef.exepath + '/../asset/font/ARCADE.TTF'), 32 )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([200, 100], self.ui._font, 'Game Design: Mass KonFuzion'), kbSelectIdx=None )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([200, 150], self.ui._font, 'Game Programming: Mass KonFuzion'), kbSelectIdx=None )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([200, 200], self.ui._font, 'Art Design (ha!): Mass KonFuzion'), kbSelectIdx=None )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([200, 250], self.ui._font, 'Game Engine: Mass KonFuzion'), kbSelectIdx=None )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([200, 300], self.ui._font, 'Music: Mass KonFuzion'), kbSelectIdx=None )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([200, 350], self.ui._font, 'Sound Effects: Mass KonFuzion'), kbSelectIdx=None )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([200, 450], self.ui._font, 'Page 2 ->'), kbSelectIdx=0, action="nextPage" )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([200, 500], self.ui._font, 'Return'), kbSelectIdx=1, action="exitUI" )
        self.ui.synchronize(0, 1)


        # Is this the "best" way to create a second page in the credits menu? No, it's not. But it works :-D
        self.ui2 = menu_form.UIForm(engineRef=engineRef) # the LHS engineRef is the function param; the RHS engineRef is the object we're passing in
        self.ui2._font = self.ui._font
        self.ui2.addMenuItem( menu_item_label.MenuItemLabel([200, 100], self.ui2._font, 'Game engine made with:'), kbSelectIdx=None )
        self.ui2.addMenuItem( menu_item_label.MenuItemLabel([240, 140], self.ui2._font, 'Pygame'), kbSelectIdx=None )
        self.ui2.addMenuItem( menu_item_label.MenuItemLabel([240, 180], self.ui2._font, 'Python 2.7'), kbSelectIdx=None )
        self.ui2.addMenuItem( menu_item_label.MenuItemLabel([200, 250], self.ui2._font, 'Other Tools Used:'), kbSelectIdx=None )
        self.ui2.addMenuItem( menu_item_label.MenuItemLabel([240, 290], self.ui2._font, 'Bfxr (sound effects)'), kbSelectIdx=None )
        self.ui2.addMenuItem( menu_item_label.MenuItemLabel([240, 330], self.ui2._font, 'LMMS (music)'), kbSelectIdx=None )
        self.ui2.addMenuItem( menu_item_label.MenuItemLabel([240, 370], self.ui2._font, 'Fonts from 1001freefonts.com'), kbSelectIdx=None )
        self.ui2.addMenuItem( menu_item_label.MenuItemLabel([200, 450], self.ui2._font, '<- Page 1'), kbSelectIdx=0, action="prevPage" )
        self.ui2.synchronize(0, 0)

        self.ui_ref = self.ui


        #Adding another DisplayMessageManager for the Title text. This is a bit hacky..
        self.title_mm = DisplayMessageManager()
        self.title_mm._font = pygame.font.Font( os.path.normpath(engineRef.exepath + '/../asset/font/ARCADE.TTF'), 64 )

        self.titleMsg = DisplayMessage()
        self.titleMsg.create(txtStr='Credits', position=[1,1], color=(192,192,192))

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
            GameStateImpl.__instance.SetName("Credits State")
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
                                  } )

    def DoUICommand(self, engineRef, argsDict):
        """
           NOTE: This function assumes argsDict has one key only: uiCommand. The value of that key dictates what to do
        """
        try:
            if argsDict['uiCommand'] == 'exitUI':
                engineRef.changeState(game_state_main_menu.GameStateImpl.Instance())
            elif argsDict['uiCommand'] == 'nextPage':
                self.ui_ref = self.ui2      # NOTE: to implement multiple pages, you can create a list of UI references, and keep a index variable
            elif argsDict['uiCommand'] == 'prevPage':
                self.ui_ref = self.ui       # NOTE: to implement multiple pages, you can create a list of UI references, and keep a index variable
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
                action = self.ui_ref.processKeyboardEvent(event, engineRef)

                if action:
                    self.EnqueueUICommandMessage(action)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                action = self.ui_ref.processMouseEvent(event, engineRef)

                if action:
                    self.EnqueueUICommandMessage(action)

            elif event.type == sound_and_music.SoundNMusicMixer.SONG_END_EVENT:
                self.mixer.loadMusicFile('Theme')
                self.mixer.playMusic()  # No matter what song was playing, load up the theme song next and play it
                                        # TODO: add config options for music on/off; if completely off, don't even play music? Right now, music plays, but if volume is 0, then of course, it's inaudible

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
        self.ui_ref.update(dt_s)

    def PreRenderScene(self, engineRef):
        pass

    def RenderScene(self, engineRef):
        self.surface_bg.fill((0,0,0))

        self.ui_ref.render(self.surface_bg)

        textSurf = self.titleMsg.getTextSurface(self.title_mm._font)
        self.surface_bg.blit(textSurf, (self.titleMsg._position[0] * self.cell_size[0], self.titleMsg._position[1] * self.cell_size[1]))
        

    def PostRenderScene(self, engineRef):
        # Flip the buffers
        pygame.display.flip()


