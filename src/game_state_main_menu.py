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
# TODO add states for a settings meun and stuff like that
# NOTE: Looks like we have to use full import names, because we have circular imports (i.e. intro state imports playing state; but playing state imports intro state. Without using full import names, we run into namespace collisions and weird stuff)

class GameStateMainMenu(game_state_base.GameStateBase):
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

        #self.mm = DisplayMessageManager()

        ## self.menuOptions = [ { 'text': 'Fall Down', 'position': [30, 30] }
        ##                    , { 'text': 'Settings', 'position': [30, 35] }
        ##                    , { 'text': 'High Scores', 'position': [30, 40] }
        ##                    , { 'text': 'Credits', 'position': [30, 45] }
        ##                    , { 'text': 'Exit', 'position': [30, 50] }
        ##                    ]
        ## self.displayMessages = []
        ## for menuOpt in self.menuOptions:
        ##     self.displayMessages.append(DisplayMessage())
        ##     self.displayMessages[len(self.displayMessages) - 1].create(txtStr=menuOpt['text'], position=menuOpt['position'], color=(192,192,192))

        ## self.selection = 0

        # TODO remove the self.menuOptions list o' dicts and associated jank. Keep the ui object instead

        self.ui = menu_form.UIForm(engineRef=engineRef) # the LHS engineRef is the function param; the RHS engineRef is the object we're passing in
        self.ui._font = menu_form.UIForm.createFontObject('../asset/font/ARCADE.TTF', 32)
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([300, 300], self.ui._font, 'Fall Down'), kbSelectIdx=0, action="startFalldown" )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([300, 350], self.ui._font, 'Settings'), kbSelectIdx=1, action="gotoSettings" )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([300, 400], self.ui._font, 'High Scores'), kbSelectIdx=2, action="TODO" )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([300, 450], self.ui._font, 'Credits'), kbSelectIdx=3, action="TODO" )
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
        if GameStateMainMenu.__instance is None:
            GameStateMainMenu.__instance = super(GameStateMainMenu, GameStateMainMenu).__new__(GameStateMainMenu)
            GameStateMainMenu.__instance.__init__()
            GameStateMainMenu.__instance.SetName("MainMenu State")
        return GameStateMainMenu.__instance
        

    # TODO Consider changing "pause" to "PushState" or something; doesn't HAVE to be 'pause'
    def Pause(self):
        # TODO check your design - you may need a pointer/reference to the engine here, to be able to push onto the stack.
        #print "GAMESTATE MainMenu State pausing"
        pass

    # TODO Consider changing "resume" to "PopState" or something; doesn't HAVE to be 'resume'
    def Resume(self):
        # TODO check your design - you may need a pointer/reference to the engine here, to be able to pop from the stack
        #print "GAMESTATE MainMenu State resume"
        pass

    def ProcessEvents(self, engineRef):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # TODO Create a quit request message, and add it to the Messaging Handler. Oh yeah, also make a Messaging Handler
                sys.exit()

            if event.type == pygame.KEYDOWN:
                ## if (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                ##     if self.selection == 0:
                ##         # NOTE: Could make class name in all game state subclasses the same; that way, we could simply code the game to look in e.g. module name "game_state_" + whatever, and call the class' Instance() method
                ##         # NOTE: Could also put the selection #s into the menu option definitions, so this if/else block wouldn't need to know which # matches up with which option; it could get that info from the menu option definition
                ##         engineRef.changeState(game_state_playing.GameStatePlaying.Instance())
                ##     elif self.selection == 1:
                ##         # Settings
                ##         engineRef.changeState(game_state_settings.GameStateSettings.Instance())
                ##     elif self.selection == 2:
                ##         # High Scores
                ##         pass
                ##     elif self.selection == 3:
                ##         # Credits
                ##         pass
                ##     elif self.selection == 4:
                ##         engineRef.isRunning = False

                ## elif (event.key == pygame.K_ESCAPE):
                ##     engineRef.changeState(game_state_intro.GameStateIntro.Instance())

                ## elif event.key == pygame.K_DOWN:
                ##     self.selection = (self.selection + 1) % len(self.displayMessages)

                ## elif event.key == pygame.K_UP:
                ##     self.selection = (self.selection - 1) % len(self.displayMessages)


                action = self.ui.processKeyboardEvent(event, engineRef)

                if action == 'startFalldown':
                    engineRef.changeState(game_state_playing.GameStatePlaying.Instance())
                elif action == 'gotoSettings':
                    engineRef.changeState(game_state_settings.GameStateSettings.Instance())
                elif action == 'exitUI':
                    engineRef.isRunning = False

                    
                    

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
        ## # NOTE: You can get away with calling getTextSurface only one time, as long as the text to be displayed doesn't change
        ## for displayMsg in self.displayMessages:
        ##     textSurf = displayMsg.getTextSurface(self.mm._font)
        ##     self.surface_bg.blit(textSurf, (displayMsg._position[0] * self.cell_size[0], displayMsg._position[1] * self.cell_size[1] ))

        self.ui.render(self.surface_bg)

        textSurf = self.titleMsg.getTextSurface(self.title_mm._font)
        self.surface_bg.blit(textSurf, (self.titleMsg._position[0] * self.cell_size[0], self.titleMsg._position[1] * self.cell_size[1]))
        

    def PostRenderScene(self, engineRef):
        # Draw a box around the selected menu item
        # NOTE: I could've put the box in the renderScene function, but the box is technically an "overlay". Also, whatever, who cares? :-D

        ## # TODO perhaps make a function in the menuform class that draws the selection (and make it customizable?)

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

