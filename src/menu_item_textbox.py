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
    def __init__(self, targetObj, keyPath, posList, fontObj):
        """Create a textbox UI object

           Textboxes are bound to config dict objects. Textboxes accept a bound config obj (the config item that contains the value to be changed) and the key (the key used to access the bound data)
        """
        super(MenuItemTextbox, self).__init__(pos=posList)
        self.bindTo(targetObj, keyPath) # bind to the supplied config dict

        self._font = fontObj    # This assigns a reference to an already-existing font object
        self._editMode = 0      # Bool - if textbox is in edit mode, its text can be edited.

        # TODO Make it possible to edit the bound value (i.e. implement the textbox functionality)
        self.setSurface( menu_item_base.MenuItemBase.createText(str(self._boundObj[self._boundItemKey]), self._font, (60,190,30)) ) # TODO: Font color should be customizable

        self._onClickFunc = self.doTopLevelClick


        # TODO The textbox should have:
        # - value/text
        # - cursor position (so we can render the cursor)
        # - cursor state (blink on / blink off)
        # - active state (editing or not editing) - note: the textbox may be selected (i.e. the active UI item on a form), but not in active edit mode
        # - render style (e.g. highlight selected text)
        # - mouse-enabled text selection (e.g. highlight the text, delete all of it; insert before other characters, etc)

        # TODO maybe set this object's onClickFunc to toggle edit/non-edit mode.

    def render(self, renderSurface):
        renderSurface.blit(self._surface, (self._position[0], self._position[1]))

    def hasSubItems(self):
        """Return True if this item has subitems; False if not"""
        return False

    def doTopLevelClick(self):
        # TODO make this function do useful stuff
        if self._editMode == 1:
            self._editMode = 0
        else:
            self._editMode = 1
        print "Textbox {} _editMode = {}".format(hex(id(self)), self._editMode)

    # TODO Make it possible to click off the textbox (e.g. on the form) and deactivate the textbox (this comment probably belongs in the form class)

    def update(self, dt_s):
        """Override the base menu item's update. The spinner needs to call update() on all its subitems
        """
        pass


