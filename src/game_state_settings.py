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

import menu_item_base
import menu_item_spinner
import menu_item_label
import menu_form

# NOTE: Looks like we have to use full import names, because we have circular imports (i.e. intro state imports playing state; but playing state imports intro state. Without using full import names, we run into namespace collisions and weird stuff)

class GameStateSettings(game_state_base.GameStateBase):
    __instance = None

    def __new__(cls):
        """Override the instantiation of this class. We're creating a singleton yeah"""
        return None

    def __init__(self):
        """ This shouldn't run.. We call __init__ on the __instance member"""
        pass

    def Init(self, engineRef):
		# Snag some vital object refs from the engine object
        self.game_size = engineRef.game_size
        self.screen_size = engineRef.screen_size
        self.cell_size = engineRef.cell_size
        self.surface_bg = engineRef.surface_bg
        self.bg_col = engineRef.bg_col


        self._eventQueue = MessageQueue() # Event queue, e.g. user key/button presses, system events
        self._eventQueue.Initialize(64)

        #self._cmdQueue = MessageQueue() # Command queue, e.g. "Start moving left"
        #self._cmdQueue.Initialize(64)

        # Register Event Listeners
        # Haha, psych! There are none

        # Register Command Listeners
        # Ditto
        
        # NOTE could optimize images by loading UI graphics at a higher level than this, e.g. to make available to all menus: main menu, settings, in-game pause, etc.
        self.uiImgCache = { 'spinner':{ 'left': menu_item_base.MenuItemBase.createImage("../asset/image/back.png")
                                      , 'right': menu_item_base.MenuItemBase.createImage("../asset/image/forward.png")
                                      }
                          }

        self.ui = menu_form.UIForm('../data/config/settings.json', engineRef=engineRef) # I hope the program understands that the engineRef on the left is the function parameter, and the one on the right is the passed-in reference
        self.ui._font = menu_form.UIForm.createFontObject('../asset/font/ARCADE.TTF', 32)
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([50,80], self.ui._font, 'Number of Tries'), kbSelectIdx=None )
        self.ui.addMenuItem( menu_item_spinner.MenuItemSpinner(self.ui._config, 'numTries', [50,120], self.ui._font, self.uiImgCache['spinner']['left'], self.uiImgCache['spinner']['right']), kbSelectIdx=0 )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([50,180], self.ui._font, 'Initial Row Spacing') )
        self.ui.addMenuItem( menu_item_spinner.MenuItemSpinner(self.ui._config, 'difficulty.initialRowSpacing', [50,220], self.ui._font, self.uiImgCache['spinner']['left'], self.uiImgCache['spinner']['right']), kbSelectIdx=1 )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([50,280], self.ui._font, 'Initial Row Grid Travel Time (seconds)') )
        self.ui.addMenuItem( menu_item_spinner.MenuItemSpinner(self.ui._config, 'difficulty.initialRowScreenClearTime', [50,320], self.ui._font, self.uiImgCache['spinner']['left'], self.uiImgCache['spinner']['right']), kbSelectIdx=2 )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([50,450], self.ui._font, 'Return'), kbSelectIdx=3, action="exitUI" )

        self.ui._kbSelection = 0 # It is necessary to set the selected item (the keyboard selection) manually. Otherwise, the UI has no way of knowing which item to interact with
        self.ui._maxKbSelection = 3 # Janky hack to know how many kb-interactive items are on the form # TODO is there a better way to specify maximum? Or maybe write an algo that figures this out?

        # TODO possibly make the menu require the user to navigate to items, and then press "enter" or something to activate the selected item for editing?

        #Adding another DisplayMessageManager for the Title text. This is a bit hacky..
        self.title_mm = DisplayMessageManager()
        self.title_mm._font = pygame.font.Font('../asset/font/ARCADE.TTF', 64)

        self.titleMsg = DisplayMessage()
        self.titleMsg.create(txtStr='Settings', position=[1,1], color=(192,192,192))

    def Cleanup(self):
        # NOTE this class is a port from a C++ class. Because Python is garbage-collected, Cleanup() is probably not necessary here. But it's included for completeness
        pass

    @staticmethod
    def Instance():
        """Return the instance reference. Create it if it doesn't exist
           
           This method is a static method because it does not use any object
        """
        if GameStateSettings.__instance is None:
            GameStateSettings.__instance = super(GameStateSettings, GameStateSettings).__new__(GameStateSettings)
            GameStateSettings.__instance.__init__()
            GameStateSettings.__instance.SetName("Settings State")
        return GameStateSettings.__instance
        

    # TODO Consider changing "pause" to "PushState" or something; doesn't HAVE to be 'pause'
    def Pause(self):
        pass

    # TODO Consider changing "resume" to "PopState" or something; doesn't HAVE to be 'resume'
    def Resume(self):
        pass

    def ProcessEvents(self, engineRef):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # TODO Create a quit request message, and add it to the Messaging Handler. Oh yeah, also make a Messaging Handler
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Note: processKeyboardEvent causes things to happen in the menu_form scope (e.g. increment/decrement values, etc).
                # Here, the action variable contains further info/instructions to process in this scope
                action = self.ui.processKeyboardEvent(event, engineRef)
                if action == 'exitUI':
                    self.ui.saveConfigToFile()
                    engineRef.changeState(game_state_main_menu.GameStateMainMenu.Instance())


            elif event.type == pygame.MOUSEBUTTONDOWN:
                action = self.ui.processMouseEvent(event, engineRef)
                # TODO perhaps put this logic into ProcessCommands, so it can be triggered via keyboard, mouse, joystick, whatever
                if action == 'exitUI':
                    self.ui.saveConfigToFile()
                    engineRef.changeState(game_state_main_menu.GameStateMainMenu.Instance())

            elif event.type == pygame.MOUSEBUTTONUP:
                action = self.ui.processMouseEvent(event, engineRef)

    def ProcessCommands(self, engineRef):
        # No command processing needed here because this is a super-simple pause state
        # However, in a more complex game, the pause menu could have more intricate controls and elements (e.g. settings menu or something), in which case command processing could be needed
        pass

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

