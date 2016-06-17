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

# Form is simply a list (or perhaps a dict)
# Each item in the list (or dict) is a Menu Item
## Also with a location on the screen (eventually should be specifiable by percentages or something, to accommodate many screen resolutions)
# Form has a bound config file (or just a bound data object)

import json
import pygame
import dot_access_dict
import menu_item_base

## TODO Find a way to keep specific game state changes out of the menu class. This class should be state-agnostic
## TODO also, probably make menu_form a base class, and then extend it for game-specific stuff.
import game_state_base
import game_state_main_menu

class UIForm(object):
    @staticmethod
    def createFontObject(fontPath, fontSize):
        return pygame.font.Font(fontPath, fontSize)

    def __init__(self, boundCfgFile=None, menuDefFile=None, engineRef=None):
        """Create a form object that is bound to the given config file
            
           boundCfgFile contains the config options to be loaded/modified/written back
           menuDefFile contains layout/definition of the UI form
        """
        # TODO -- Remove boundCfgFile? The UI form does not REQUIRE a bound config file
        #if not boundCfgFile:
        #    raise Exception("You must supply a config file (json) that is bound to this form")

        self._uiItems = []

        self._config = None         # The dict that holds the configuration that this menu is controlling
        self._activeMenuItem = None # The active menu item (e.g. a spinner, label, button, etc.)
        self._activeSubItem = None  # The active menu item's active sub-item (e.g. a spinner's left arrow)
        self._font = None           # Font object for the form TODO - use a list? Possibly move into a FormManager class? (e.g. a FontManager could contain many forms, for multi-screen menus; and also, could manage all the font objects and what not)
        self._fontColor = None
        self._engineRef = engineRef # TODO delete this if we end up not using it; may be obviated by pass-through actions (pass the action instruction back to the calling scope instead of executing it here in this scope)
        self._kbSelection = None    # The index # of the item selected by keyboard input
        self._maxKbSelection = None

        if boundCfgFile:
            self._configFile = boundCfgFile     # The file name -- use this when reading and writing the file
            self.loadConfigFromFile()
        else:
            self._configFile = None

        if menuDefFile:
            # TODO implement this -- load menu definition from json (or otherwise, delete this whole block)
            # Maybe call a function to load from json?
            pass
        else:
            # TODO don't hardcode menu definition? Right now, menu is hardcoded and passed into this constructor
            # NOTE: Right now, the menuDefFile is entirely unsed. And the menu items are defined outside the scope of this class
            pass

    # TODO probably change loadConfigFromFile() to take in the filename, and remove the bound config file from the constructor. Or otherwise, keep the ctor as-is, and add an optional arg to the load function, to allow developer to choose
    def loadConfigFromFile(self):
        """Load config from the file specified in the constructor of this object"""
        with open(self._configFile, 'r+') as fd:
            # TODO add error checking (e.g. IOError)?
            tmpDict = json.load(fd)
            self._config = dot_access_dict.DotAccessDict(tmpDict)

    def saveConfigToFile(self):
        """Save config back to file specified in the constructor of this object"""
        with open(self._configFile, 'w') as fd:
            json.dump(self._config, fd)

    def processMouseEvent(self, event, engineRef):
        """Process mouse event

           Events are Pygame events
           engineRef is provided in case it is needed
        """
        # TODO Make it possible for the UI to know where the "cursor" is, and to be able to move the cursor with the mouse, joystick, whatever. Also, the UI should respond to button presses on the keyboard, mouse, joystick, whatever
        # TODO update UI event handling to be more modular -- e.g. this UI form should call functions to handle a "button press" regardless of what input device generated the input
        if event.type == pygame.MOUSEBUTTONDOWN:
            for uiItem in self._uiItems:
                mousePos = pygame.mouse.get_pos()
                pressedButtons = pygame.mouse.get_pressed() # [0] = left; [1] = middle; [2] = right
                timeStamp = pygame.time.get_ticks() / 1000.0 # get timestamp; convert to seconds
                ##print "Clicked a button: {}, coord:{}, time:{}".format(pressedButtons, mousePos, timeStamp)

                # NOTE: This is the composite spinner object (the item can be contained in a list of objects or whatever)
                # TODO - form controls should be in a list/array
                # TODO add mouse-in-bounds test for label items. Even though they don't respond to mouse clicks, it might be useful (esp to make buttons, which are, essentially, labels with an action)
                # TODO Have a function callback of some sort for each UI Item type, and call it. Spinners can have an internal subitem collision check; labels can execute a command; other items can do (or not do) actions, based on context.
                if uiItem['uiItem'].isMouseWithinBounds(mousePos): 
                    ##print "Mouse click button {} on object id:{}".format(event.button, id(uiItem))
                    # TODO perhaps separate the setting of the active item (during collection phase) from the handling (e.g. setting initial timer)/update
                    # TODO send a key/button press to the object (perhaps the object can have a queue of timestamped inputs, to process and look for double-clicks, etc)
                    self._activeMenuItem = uiItem['uiItem']   # activeMenuItem is a variable that maybe can belong to a top-level UI manager object thingamajig
                    
                    # TODO: implement the following function call; it should be the only function call in this scope (i.e., delete the stuff below it to the next elif block
                    # self._activeMenuItem.processMouseEvent(mousePos) # This function should set a state, and/or execute a function

                    # ============= TODO Query the spinner for a subitem, to set the mouse state ==========
                    # TODO maybe we should change the onClickFuncs to take in the event, timestamp, etc
                    self._activeMenuItem.setMouseButtonState(event.button - 1, menu_item_base.UIItemState.mouseButtonDown, pygame.time.get_ticks() / 1000.0)
                    self._activeMenuItem.setMousePosition(mousePos)

                    if self._activeMenuItem._onClickFunc:
                        # TODO perhaps the clickFuncs should take in the mouse position and button states? Or otherwise, the onClickFuncs should NOT take those, but should USE them, after they've been set elsewhere (e.g. in setMouseButtonState, setMousePosition, etc)?
                        self._activeMenuItem._onClickFunc() 

            # TODO Detect that the user clicked e.g. in menu whitespace, and set self._activeMenuItem to None
            # TODO Detect that the user clicked e.g. in menu whitespace, and set self._activeSubItem to None
            # OR... TODO do away with _activeSubItem? Really, the main form should not know about subitems; only top-level items. If a top-level item has subitems, it should handle them internally

        elif event.type == pygame.MOUSEBUTTONUP:
            if self._activeMenuItem:
                # Unset whatever button was pressed (i.e. unset mouse tracking var of active menu item
                self._activeMenuItem.setMouseButtonState(event.button - 1, menu_item_base.UIItemState.mouseButtonUp, pygame.time.get_ticks() / 1000.0)

    def processKeyboardEvent(self, event, engineRef):
        """Process keyboard event

           Events are Pygame events
           engineRef is provided in case it is needed
        """
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                # Confirm selection -- take action
                uiItem = self.getKBActiveItem()
                if uiItem:
                    # TODO maybe rename this to "passThruAction" or something. We're going to simply pass the input value through as a return value, to allow the calling scope to execute an action
                    if uiItem['action']:
                        ## # Note: uiItem should be something.. It should not be None. If it's None, that means something bad happened
                        return uiItem['action']


            if event.key == pygame.K_ESCAPE:
                self.saveConfigToFile()
                self._engineRef.changeState(game_state_main_menu.GameStateMainMenu.Instance())

            elif event.key == pygame.K_DOWN:
                self._kbSelection += 1
                if self._kbSelection > self._maxKbSelection:
                    self._kbSelection = 0

            elif event.key == pygame.K_UP:
                self._kbSelection -= 1
                if self._kbSelection < 0:
                    self._kbSelection = self._maxKbSelection

            ### if event.type == pygame.KEYDOWN:
            ###     if (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
            ###         if self.selection == 0:
            ###             # NOTE: Could make class name in all game state subclasses the same; that way, we could simply code the game to look in e.g. module name "game_state_" + whatever, and call the class' Instance() method
            ###             # NOTE: Could also put the selection #s into the menu option definitions, so this if/else block wouldn't need to know which # matches up with which option; it could get that info from the menu option definition
            ###             # TODO 
            ###             #engineRef.changeState(game_state_playing.GameStatePlaying.Instance())
            ###             pass
            ###         elif self.selection == 1:
            ###             # Screen size
            ###             pass
            ###         elif self.selection == 2:
            ###             # Sound volume
            ###             pass
            ###         elif self.selection == 3:
            ###             # Music volume
            ###             pass
            ###         elif self.selection == 4:
            ###             engineRef.changeState(game_state_main_menu.GameStateMainMenu.Instance())

            ###     elif (event.key == pygame.K_ESCAPE):
            ###         self.ui.saveConfigToFile()
            ###         engineRef.changeState(game_state_main_menu.GameStateMainMenu.Instance())

            ###     elif event.key == pygame.K_DOWN:
            ###         # TODO no sir... handle the key in the UI
            ###         self.ui._kbSelection += 1
            ###         if self.ui._kbSelection > self.ui._maxKbSelection:
            ###             self.ui._kbSelection = 0
            ###             
            ###     elif event.key == pygame.K_UP:
            ###         self.ui._kbSelection -= 1
            ###         if self.ui._kbSelection < 0:
            ###             self.ui._kbSelection = self.ui._maxKbSelection

    def getKBActiveItem(self):
        for uiItem in self._uiItems:
            if uiItem['kbSelectIdx'] == self._kbSelection:
                return uiItem
        return None

    def addMenuItem(self, uiItem, kbSelectIdx=None, action=None):
        """Add a UI menu item to this form's list of UI items
        """
        # TODO -- make this a dict. Add a flag for keyboard-interactive (i.e., anything could theoretically respond to the mouse/joystick, , but we have to include info about what's interactive with the keyboard
        self._uiItems.append( {'uiItem': uiItem, 'kbSelectIdx': kbSelectIdx, 'action': action} )
        # kbSelectIdx tells the item how to interact with the keyboard. The index # is the number in the list of keyboard-interactive items
        # Action is a function call -- it is used to make Labels have executable commands (but perhaps we should make a new type of UI item called CommandButton, and simplify labels

    def update(self, dt_s):
        """Update
        """
        #TODO (only update the active item? All items?)
        for uiItem in self._uiItems:
            uiItem['uiItem'].update(dt_s)

    def render(self, renderSurface):
        for uiItem in self._uiItems:
            uiItem['uiItem'].render(renderSurface)

            if uiItem['kbSelectIdx'] == self._kbSelection:
                # TODO make this kb selection rectangle surround the item it's highlighting. I'm allowing jank in because I want to quickly test it.
                pygame.draw.rect(renderSurface, (192,128,0), (10, uiItem['uiItem']._position[1], 30, 30), 2)

