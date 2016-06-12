# Spinner = form control with a value, and a left/right (or also TODO up/down?) clickable arrows. Click the arrows to change the value

import menu_item_base
import pygame


class MenuItemSpinner(menu_item_base.MenuItemBase):
    def __init__(self, configDict, configKey, posList, fontObj, leftArrowImageSurf, rightArrowImageSurf):
        # TODO make posX,posY a list/tuple? (to be consistent with the base class constructor?)
        super(MenuItemSpinner, self).__init__(pos=posList)
        # TODO fix stuff -- this class may need only to be a container class of MenuItemBase objects.. It may not need to BE a MenuItemBase derivative? I'm not sure. I suck at software design

        self.bindTo(configDict, configKey) # bind to the supplied config dict

        self._subItems = [] # To be filled: [0] = left arror; [1] = text; [2] = right arrow
        for i in xrange(0, 3):
            self._subItems.append( menu_item_base.MenuItemBase() )

        self._subItems[0] = menu_item_base.MenuItemBase() #initialize left arrow
        self._subItems[0].setSurface( leftArrowImageSurf )
        #self._subItems[0].setOnClickFunc( lambda boundVal: boundVal - 1 ) # TODO modify this function def as appropriate
        self._subItems[0].setOnClickFunc( self.decrementBoundVal ) # TODO modify this function def as appropriate

        self._subItems[1] = menu_item_base.MenuItemBase()
        self._subItems[1]._font = fontObj   # This assigns a reference to an already-existing font object
        # TODO - don't hardcode the text color
        self._subItems[1].setSurface( menu_item_base.MenuItemBase.createText(str(self._boundObj[self._boundItemKey]), self._subItems[1]._font, (255,255,255)) )

        self._subItems[2] = menu_item_base.MenuItemBase()
        self._subItems[2].setSurface( rightArrowImageSurf )
        #self._subItems[2].setOnClickFunc( lambda boundVal: boundVal + 1 ) # TODO modify this function def as appropriate
        self._subItems[2].setOnClickFunc( self.incrementBoundVal ) # TODO modify this function def as appropriate

        #TODO perhaps be a little smarter about how we compute the size of the parent spinner object?

        self.recalculateSubItems()

        # TODO: Make a class called ClickableBase, and also 2 subclasses: ClickableImage and ClickableText.  The classes will have functions to detect mousee clicks; the Text will be a text box (e.g., for the spinner value), and the image will have icons/images (for the arrow pictures, or whatever other form elements we want to support)

        # TODO: When making composite items (e.g. spinner, which has probably 3 image surfaces (2 for arrow images/icons, and 1 for text), the sub-items will be blitted onto the top-level item's surface, and then the top-level's surface will be blitted onto to the screen

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
        # TODO consider incorporating selectedSubItem into the base class (using raise NotImplementedError)
        for subItem in self._subItems:
            if subItem.isMouseWithinBounds(mouse_pos):
                return subItem


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
        # TODO: Make it possible to process deeper-level items in the config dict. e.g., You can use a loop or something. See your leftover stack overflow browser tabs/history

        self._boundObj[self._boundItemKey] -= 1
        self._subItems[1].setSurface( menu_item_base.MenuItemBase.createText(str(self._boundObj[self._boundItemKey]), self._subItems[1]._font, (255,255,255)) )
        self.recalculateSubItems()

    def incrementBoundVal(self):
        self._boundObj[self._boundItemKey] += 1
        self._subItems[1].setSurface( menu_item_base.MenuItemBase.createText(str(self._boundObj[self._boundItemKey]), self._subItems[1]._font, (255,255,255)) )
        self.recalculateSubItems()

        # NOTE: It seems wasteful to create a new surface every time we change text... But I don't know a better way...
