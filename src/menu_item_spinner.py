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

# Spinner = form control with a value, and a left/right (or also TODO up/down?) clickable arrows. Click the arrows to change the value

# TODO - add an increment/decrement amount (e.g. +/- 1, +/- 0.1, whatever), and a min/max value

import menu_item_base
import pygame


class MenuItemSpinner(menu_item_base.MenuItemBase):
    def __init__(self, targetObj, keyPath, posList, fontObj, leftArrowImageSurf, rightArrowImageSurf, locked=False):
        super(MenuItemSpinner, self).__init__(pos=posList)
        self._locked = locked   # By default, a spinner is unlocked.

        self.bindTo(targetObj, keyPath) # bind to the supplied config dict

        self._subItems = [] # To be filled: [0] = left arror; [1] = text; [2] = right arrow

        # Initialize subitems (TODO perhaps put subitem init into a function?)
        for i in xrange(0, 3):
            self._subItems.append( menu_item_base.MenuItemBase() )

        self._subItems[0] = menu_item_base.MenuItemBase() #initialize left arrow
        self._subItems[0].setSurface( leftArrowImageSurf )
        self._subItems[0].setOnClickFunc( self.decrementBoundVal )

        self._subItems[1] = menu_item_base.MenuItemBase()
        self._subItems[1]._font = fontObj   # This assigns a reference to an already-existing font object
        # TODO - don't hardcode the text color
        self._subItems[1].setSurface( menu_item_base.MenuItemBase.createText(str(self._boundObj[self._boundItemKey]), self._subItems[1]._font, (255,255,255)) )

        self._subItems[2] = menu_item_base.MenuItemBase()
        self._subItems[2].setSurface( rightArrowImageSurf )
        self._subItems[2].setOnClickFunc( self.incrementBoundVal )

        self.recalculateSubItems()

        # Set this item's own onClickFunc
        self._onClickFunc = self.doTopLevelClick


    def recalculateSubItems(self):
        """ Recalculate the sizes/positions of the subitems; update the size of the composite object, as well
        """
        # Subitems
        self._subItems[0].setPosition( self._position[0], self._position[1] )
        self._subItems[1].setPosition( self._subItems[0]._position[0] + self._subItems[0]._surface.get_size()[0] + 1, self._position[1] )
        self._subItems[2].setPosition( self._subItems[1]._position[0] + self._subItems[1]._surface.get_size()[0] + 1, self._position[1] )

        # Composite object
        self._size[0] = self._subItems[0]._size[0] + self._subItems[1]._size[0] + self._subItems[2]._size[0]
        self._size[1] = self._subItems[0]._size[1]

    def selectedSubItem(self, mouse_pos):
        """Return the selected subitem, based on mouse position

           This function is only called if the mouse has been clicked on this item.
           This function must be implemented if the menu item has subitems (because the UI Form class will call it
        """
        # TODO consider incorporating selectedSubItem into the base class (using raise NotImplementedError)
        for subItem in self._subItems:
            if subItem.isMouseWithinBounds(mouse_pos):
                return subItem

    def hasSubItems(self):
        """Return True if this item has subitems; False if not"""
        return True

    def render(self, renderSurface):
        for subItem in self._subItems:
            # The real drawing
            renderSurface.blit(subItem._surface, (subItem._position[0], subItem._position[1]))
        ##    # TODO the stuff below is debug stuff and can probably be deleted (or commented out)
        ##    pygame.draw.rect(renderSurface, (0,64,128), ( subItem._position[0], subItem._position[1], subItem._surface.get_size()[0], subItem._surface.get_size()[1] ), 1)
        ##    pygame.draw.rect(renderSurface, (192,64,64), ( 100, 100, 4, 4 ), 2)
        ##pygame.draw.rect(renderSurface, (0, 128, 255), ( self._position[0], self._position[1], self._size[0], self._size[1]  ), 1)

    def update(self, dt_s):
        """Override the base menu item's update. The spinner needs to call update() on all its subitems
        """
        for subItem in self._subItems:
            subItem.update(dt_s)

    def decrementBoundVal(self):
        self._boundObj[self._boundItemKey] -= 1
        self._subItems[1].setSurface( menu_item_base.MenuItemBase.createText(str(self._boundObj[self._boundItemKey]), self._subItems[1]._font, (255,255,255)) )
        self.recalculateSubItems()

    def incrementBoundVal(self):
        self._boundObj[self._boundItemKey] += 1
        self._subItems[1].setSurface( menu_item_base.MenuItemBase.createText(str(self._boundObj[self._boundItemKey]), self._subItems[1]._font, (255,255,255)) )
        self.recalculateSubItems()

        # NOTE: It seems wasteful to create a new surface every time we change text... But I don't know a better way...

    def doTopLevelClick(self):
        """ Handle mouse clicks to determine where they fell, and what should happen"""
        ## self._activeSubItem = uiItem['uiItem'].selectedSubItem(self._mousePos)    # activeSubItem is a variable that maybe can belong to a top-level UI manager object thingamajig. This came from the top-level form. Do we need it?
        activeSubItem = self.selectedSubItem(self._mousePos)
        if activeSubItem:
            activeSubItem._onClickFunc()
        # Because the spinner is initialized with a bound value, which is managed internally, onClickFunc does not need to pass in any parameters

    def setMouseButtonState(self, buttonID, state, timestamp):
        """Override setMouseButtonState from the base class"""
        ##print "menu_item_base.setMouseButtonState({},{},{})".format(buttonID, state, timestamp)
        self._mouseButtonState[buttonID]['state'] = state
        self._mouseButtonState[buttonID]['timestamp'] = timestamp
        
        # Reset the elapsed time counter on mouseButtonUp (there's probably a better way to design this..)
        if state == menu_item_base.UIItemState.mouseButtonUp:
            self._mouseButtonState[buttonID]['elapsedTime'] - 0.0
        ##print "Item {} mouseButtonState: {}".format(id(self), self._mouseButtonState)

            # TODO: fix your busted design
            if self._subItems:  # This test should always pass and actually should be removed (TODO)
                # NOTE: This is janky - design a better way to track the state of subItems
                for subItem in self._subItems:
                    subItem.setMouseButtonState(buttonID, state, timestamp)
