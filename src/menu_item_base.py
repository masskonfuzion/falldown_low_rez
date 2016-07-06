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

# Base class items should have:
# Position (position on screen where to draw the item)
# Value (var to store the value of the bound config option)
# Bound Value (controlled by a config of some sort: mapping of menu/form items to config data points)
## Map the menu item to the config
# Image (optional image file)

# Subclasses should have:
# Control type (e.g. textbox, spinner (e.g. click up/down, or left/right icons to change value, checkbox)

# Configs are just a json object

# TODO - perhaps move all of the logic that makes this base item clickable into a subclass?

import pygame

# TODO add a cache of image files for different click states. e.g. Left Arrow, clicked; Left arrow unclicked. The cache should belong to the form itself; any objects that use those images can use the cached image.
class UIItemState(object):
    # Static stuff -- essentially an enum
    mouseButtonUp = 0
    mouseButtonDown = 1

class MenuItemBase(object):
    # Static variables used by UI
    doubleTapInterval = 0.2 # Time interval (in seconds) in which to look for a 2nd key/button press
    longPressDelay = 0.4    # Amt of time (in sec) with key/button down, to consider interaction a "long press"
    retriggerDelay = 0.2    # Amt of time (in sec), with key/button down, in "long press" state, to wait before retriggering action
    validTextboxKeycodes = [8,9,13] + [x for x in range(32, 128) ]  # valid keycodes for textbox text entry

    @staticmethod
    def createText(textStr, fontObj=None, fontColor=None, surfSize=None):
        """Load text (in Pygame, return a surface object)
           Assumes that fontObj has already been created. (Otherwise, will raise exception)
        """


        color = fontColor if fontColor else (255,255,255)

        # TODO make the sizer surface customizable
        initSize = surfSize if surfSize else fontObj.size(textStr)
        bgSizerSurf = pygame.surface.Surface(initSize)
        bgSizerSurf.blit(fontObj.render(textStr, True, color), (0,0))
        return bgSizerSurf

    @staticmethod
    def createImage(imgPath):
        """Load an image (in Pygame, return a surface object)
           Implement as a static method so any object with access to the class can get an image (whether it's a menu item, or a subitem
        """
        return pygame.image.load(imgPath)

    def __init__(self, pos=None,size=None,surface=None):
        """Initialize a MenuItemBase obj
           
        """
        # We've done some janky initializations to force Python to create new pos/size objects. Otherwise, Python would "optimize" performance by giving multiple MenuItemBase objects references to the same position obj.. That caused weird results.
        self._position = pos if pos else [0,0]  # render position on screen
        self._size = size if size else [32,32]  # Default to 32x32
        self._value = None          # config value # NOTE: We might not need this -- UI elements are bound to objects outside the UI element itself (e.g. a config dict
        self._boundObj = None       # Reference to config obj (e.g. dict)
        self._boundItemKey = ''     # String containing key/path of item to be controlled by this UI item
        self._surface = surface     # Pygame/SDL surface for, e.g., image/icon/text rendering
        self._onClickFunc = None    # TODO consider making skeleton function defs here? (so that the developer can know what the function signatures for the on-whatever-event functions should look like)
        self._onKeyFunc = None
        self._locked = True         # Locked for editing (Note: this property is overridden by the constructors of subclasses)

        # mouseButtonState is the instantaneous state (not considering history)
        self._mouseButtonState = [ { "state": UIItemState.mouseButtonUp, "timestamp": 0.0, "elapsedTime": 0.0 } # left button
                                 , { "state": UIItemState.mouseButtonUp, "timestamp": 0.0, "elapsedTime": 0.0 } # middle button
                                 , { "state": UIItemState.mouseButtonUp, "timestamp": 0.0, "elapsedTime": 0.0 } # right button
                                 ]

        self._mousePos = [0,0]

    def setMouseButtonState(self, buttonID, state, timestamp):
        # TODO Remove default implementation and make setMouseButtonState raise NotImplementedError?
        ##print "menu_item_base.setMouseButtonState({},{},{})".format(buttonID, state, timestamp)
        self._mouseButtonState[buttonID]['state'] = state
        self._mouseButtonState[buttonID]['timestamp'] = timestamp
        
        # Reset the elapsed time counter on mouseButtonUp (there's probably a better way to design this..)
        if state == UIItemState.mouseButtonUp:
            self._mouseButtonState[buttonID]['elapsedTime'] - 0.0
        ##print "Item {} mouseButtonState: {}".format(id(self), self._mouseButtonState)

    def setMousePosition(self, mouse_pos):
        """Set the mouse position (usually in the context of the mouse cursor's position at the time of a click or other event
           mouse_pos is a pygame tuple, created by pygame.mouse.get_pos()
        """
        self._mousePos[0] = mouse_pos[0]
        self._mousePos[1] = mouse_pos[1]

    def hasSubItems(self):
        """Return True if this item has subitems; False if not
        """
        raise NotImplementedError

    def bindTo(self, targetObj, keyPath):
        """Assign self._boundObj to target. Target should be a pointer/reference to the data object this menu
           item will control

           NOTE: The bound object is, e.g. a reference to a dict. We bind to the dict so that changes we make
           to its items will be changed on the object itself. If we were to pass in an int or something, Python
           would make a copy (i.e., Python does some implicit pass-by-reference vs pass-by-value to functions)
        """
        self._boundObj = targetObj
        self._boundItemKey = keyPath

    def setValue(self, newVal):
        """Set the value of this menu item (to be written back to the config object when
           the menu is closed/saved.
        """
        self._value = newVal

    def setSurface(self, surfObj):
        """Set this object's surface object, and also compute its size.

           NOTE: You definitely want to call this function instead of setting _surface directly
        """
        self._surface = surfObj
        temp_size = self._surface.get_size()
        self._size[0] = temp_size[0]
        self._size[1] = temp_size[1]

    def setPosition(self, x, y):
        self._position[0] = x
        self._position[1] = y

    def setOnClickFunc(self, fnPtr):
        self._onClickFunc = fnPtr

    def isMouseWithinBounds(self, mouse_pos):
        if mouse_pos[0] < self._position[0] or mouse_pos[0] > self._position[0] + self._size[0]:
            return False
        if mouse_pos[1] < self._position[1] or mouse_pos[1] > self._position[1] + self._size[1]:
            return False
        return True

    def update(self, dt_s):
        """Update stuff
           Example: perhaps 'listen' for long presses by counting how long a button has been held down
        """
        # Compute the amt of time a button state has been active, using the given mouseButtonState tuple
        for buttonState in self._mouseButtonState:
            if buttonState['state'] == UIItemState.mouseButtonDown:
                buttonState['elapsedTime'] += dt_s
                #print "Menu item {} buttonState{}".format(id(self), self._mouseButtonState)
                # When elapsed time > longPressDelay, then the button is to be considered held
                # TODO perhaps put all these button states into a mouse controller class and/or keyboard controller class, instead of menu item?

            if buttonState['elapsedTime'] > MenuItemBase.longPressDelay:
                # TODO trigger a long press action? Perhaps enqueue a message?
                pass

