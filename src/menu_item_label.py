# Label = form control with a text display (technically, it's not a "control" -- it's just a label :-D)

import menu_item_base
import pygame

class MenuItemLabel(menu_item_base.MenuItemBase):
    def __init__(self, posList, fontObj, text):
        # TODO make posX,posY a list/tuple? (to be consistent with the base class constructor?)
        super(MenuItemLabel, self).__init__(pos=posList)
        # TODO maybe create a font object outside of this class and pass it in.. It's wasteful to have each object load its own font obj (e.g. a label, and also a spinner). The label can belong to the menu/form object. Or to the static class?? Basically, just somewhere else
        self._font = fontObj    # This assigns a reference to an already-existing font object
        self.setSurface( menu_item_base.MenuItemBase.createText(text , self._font, (255,255,255)) )

    def render(self, renderSurface):
        renderSurface.blit(self._surface, (self._position[0], self._position[1]))

