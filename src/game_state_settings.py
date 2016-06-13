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
        
        self.uiImgCache = { 'spinner':{ 'left': menu_item_base.MenuItemBase.createImage("../asset/image/back.png")
                                      , 'right': menu_item_base.MenuItemBase.createImage("../asset/image/forward.png")
                                      }
                          }

        self.ui = menu_form.UIForm('../data/config/settings.json')
        self.ui._font = menu_form.UIForm.createFontObject('../asset/font/ARCADE.TTF', 32)
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([50,80], self.ui._font, 'Number of Tries'), kbSelectIdx=None )
        self.ui.addMenuItem( menu_item_spinner.MenuItemSpinner(self.ui._config, 'numTries', [50,120], self.ui._font, self.uiImgCache['spinner']['left'], self.uiImgCache['spinner']['right']), kbSelectIdx=0 )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([50,180], self.ui._font, 'Initial Row Spacing') )
        self.ui.addMenuItem( menu_item_spinner.MenuItemSpinner(self.ui._config, 'difficulty.initialRowSpacing', [50,220], self.ui._font, self.uiImgCache['spinner']['left'], self.uiImgCache['spinner']['right']), kbSelectIdx=1 )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([50,280], self.ui._font, 'Initial Row Grid Travel Time (seconds)') )
        self.ui.addMenuItem( menu_item_spinner.MenuItemSpinner(self.ui._config, 'difficulty.initialRowScreenClearTime', [50,320], self.ui._font, self.uiImgCache['spinner']['left'], self.uiImgCache['spinner']['right']), kbSelectIdx=2 )

        self.selection = 0

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
        # TODO check your design - you may need a pointer/reference to the engine here, to be able to push onto the stack.
        #print "GAMESTATE Settings State pausing"
        pass

    # TODO Consider changing "resume" to "PopState" or something; doesn't HAVE to be 'resume'
    def Resume(self):
        # TODO check your design - you may need a pointer/reference to the engine here, to be able to pop from the stack
        #print "GAMESTATE Settings State resume"
        pass

    def ProcessEvents(self, engineRef):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # TODO Create a quit request message, and add it to the Messaging Handler. Oh yeah, also make a Messaging Handler
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                    if self.selection == 0:
                        # NOTE: Could make class name in all game state subclasses the same; that way, we could simply code the game to look in e.g. module name "game_state_" + whatever, and call the class' Instance() method
                        # NOTE: Could also put the selection #s into the menu option definitions, so this if/else block wouldn't need to know which # matches up with which option; it could get that info from the menu option definition
                        # TODO 
                        #engineRef.changeState(game_state_playing.GameStatePlaying.Instance())
                        pass
                    elif self.selection == 1:
                        # Screen size
                        pass
                    elif self.selection == 2:
                        # Sound volume
                        pass
                    elif self.selection == 3:
                        # Music volume
                        pass
                    elif self.selection == 4:
                        engineRef.changeState(game_state_main_menu.GameStateMainMenu.Instance())

                elif (event.key == pygame.K_ESCAPE):
                    self.ui.saveConfigToFile()
                    engineRef.changeState(game_state_main_menu.GameStateMainMenu.Instance())

                ## elif event.key == pygame.K_DOWN:
                ##     self.selection = (self.selection + 1) % len(self.displayMessages)

                ## elif event.key == pygame.K_UP:
                ##     self.selection = (self.selection - 1) % len(self.displayMessages)


            #TODO update the UI to be able to handle keyboard events, as well as mouse events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.ui.processMouseEvent(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.ui.processMouseEvent(event)


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

        ## # Janky hardcoding here... TODO fix the jankiness
        ## for displayMsg in self.displayMessages:
        ##     textSurf = displayMsg.getTextSurface(self.mm._font)
        ##     self.surface_bg.blit(textSurf, (displayMsg._position[0] * self.cell_size[0], displayMsg._position[1] * self.cell_size[1] ))

        # Render the title text surface
        textSurf = self.titleMsg.getTextSurface(self.title_mm._font)
        self.surface_bg.blit(textSurf, (self.titleMsg._position[0] * self.cell_size[0], self.titleMsg._position[1] * self.cell_size[1]))

        # Render the UI
        self.ui.render(self.surface_bg)

    def PostRenderScene(self, engineRef):
        # Draw a box around the selected menu item
        # NOTE: I could've put the box in the renderScene function, but the box is technically an "overlay". Also, whatever, who cares? :-D

        ## dispMsgRef = self.displayMessages[self.selection]

        ## #TODO easy optimization: compute and store the font rendering size
        ## selectRect = ( (dispMsgRef._position[0] - 1) * self.cell_size[0]
        ##              , (dispMsgRef._position[1] - 1) * self.cell_size[1]
        ##              , self.mm._font.size(dispMsgRef._text + "  ")[0]
        ##              , self.mm._font.size(dispMsgRef._text)[1]
        ##              )

        ## pygame.draw.rect(self.surface_bg, (192,128,0), selectRect, 2)
        # Flip the buffers

        pygame.display.flip()

