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

# Label = form control with a text display (technically, it's not a "control" -- it's just a label :-D)

import menu_item_base
import pygame

class MenuItemTextbox(menu_item_base.MenuItemBase):
    def __init__(self, targetObj, keyPath, posList, fontObj, locked=False):
        """Create a textbox UI object

           Textboxes are bound to config dict objects. Textboxes accept a bound config obj (the config item that contains the value to be changed) and the key (the key used to access the bound data)
        """
        super(MenuItemTextbox, self).__init__(pos=posList)
        self.bindTo(targetObj, keyPath) # bind to the supplied config dict

        self._font = fontObj    # This assigns a reference to an already-existing font object
        self._editMode = 0      # Bool - if textbox is in edit mode, its text can be edited.
        self._locked = locked

        # TODO Make it possible to edit the bound value (i.e. implement the textbox functionality)
        self.setSurface( menu_item_base.MenuItemBase.createText(str(self._boundObj[self._boundItemKey]), self._font, (60,190,30)) ) # TODO: Font color should be customizable

        self._onClickFunc = self.doTopLevelClick
        self._onKeyFunc = self.processKeyboardInput


        # TODO The textbox should have:
        # - value/text
        # - cursor position (so we can render the cursor)
        # - cursor state (blink on / blink off)
        # - active state (editing or not editing) - note: the textbox may be selected (i.e. the active UI item on a form), but not in active edit mode
        # - render style (e.g. highlight selected text)
        # - mouse-enabled text selection (e.g. highlight the text, delete all of it; insert before other characters, etc)

    def render(self, renderSurface):
        renderSurface.blit(self._surface, (self._position[0], self._position[1]))
        if self._editMode:
            hlSize = self._surface.get_size()
            margin = 10
            hlRect = ( self._position[0] - margin, self._position[1] - margin, hlSize[0] + margin, hlSize[1] + margin )

            pygame.draw.rect(renderSurface, (0, 64, 128), hlRect, 2)

    def hasSubItems(self):
        """Return True if this item has subitems; False if not"""
        return False

    def doTopLevelClick(self):
        if not self._locked:
            self._editMode = (self._editMode + 1) % 2
        #print "Textbox {} _editMode = {}".format(hex(id(self)), self._editMode)

    def processKeyboardInput(self, event):
        """Process keyboard event

           event is a pygame keyboard event (passed in by the caller)
        """
        if self._locked:
            return

        if self._editMode == 1:
            #print "Textbox {} key pressed was keycode:{} scancode:{} unicode:{}".format(hex(id(self)), event.key, event.scancode, event.unicode)

            if event.key == pygame.K_BACKSPACE:
                boundObjVal = self._boundObj[self._boundItemKey]    # Use this var to reduce the # of calls to self._boundObj.__getitem__
                #print "menu_item_textbox: Removing a char (makes 1 call to __getitem__ and 1 call to __setitem__)"
                self._boundObj[self._boundItemKey] = unicode(boundObjVal[:len(boundObjVal) - 1])   # Take the slice of the string that's 1 less than its length (this assumes text data; won't work if, for some reason, this textbox is bound to a non-string item)
            elif event.key in menu_item_base.MenuItemBase.validTextboxKeycodes:
                #print "menu_item_textbox: Adding {} to bound value".format(event.unicode)
                self._boundObj[self._boundItemKey] += event.unicode     # Append the typed char to the string (NOTE: assumes string data)

            #print "menu_item_textbox: boundObj (BEFORE surface update) = {}".format(self._boundObj)
            #print "menu_item_textbox: Updating the textbox surface"

            # TODO: Font color should be customizable; TODO - BS spacer size should be customized by a property of the form or something.
            # Note: the call to font.size('A') simply gets the height of a character, to create the spacer surface. We use a spacer so that the createText() call does not attempt to call size() on a potentially empty string. Doing so seems mess things up.
            #newSurf = menu_item_base.MenuItemBase.createText( str(self._boundObj[self._boundItemKey]), fontObj=self._font, fontColor=(60,190,30), surfSize=(400, self._font.size('A')[1]) )
            newSurf = menu_item_base.MenuItemBase.createText( str(self._boundObj[self._boundItemKey]), fontObj=self._font, fontColor=(60,190,30) ) # This version auto-sizes the textbox. Works, but can look bad if you outline the box
            self.setSurface( newSurf )

            #print "menu_item_textbox: boundObj (AFTER surface update) = {}".format(self._boundObj)

        else:
            #print "Textbox not in edit mode. Go away :-D"
            pass

    # TODO Make it possible to click off the textbox (e.g. on the form) and deactivate the textbox (this comment probably belongs in the form class)

    def update(self, dt_s):
        """Override the base menu item's update. The spinner needs to call update() on all its subitems
        """
        pass


