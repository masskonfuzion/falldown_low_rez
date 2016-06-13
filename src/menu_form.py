# Form is simply a list (or perhaps a dict)
# Each item in the list (or dict) is a Menu Item
## Also with a location on the screen (eventually should be specifiable by percentages or something, to accommodate many screen resolutions)
# Form has a bound config file (or just a bound data object)

import json
import pygame
import dot_access_dict
import menu_item_base

class UIForm(object):
    @staticmethod
    def createFontObject(fontPath, fontSize):
        return pygame.font.Font(fontPath, fontSize)

    def __init__(self, boundCfgFile=None, menuDefFile=None):
        """Create a form object that is bound to the given config file
            
           boundCfgFile contains the config options to be loaded/modified/written back
           menuDefFile contains layout/definition of the UI form
        """
        if not boundCfgFile:
            raise Exception("You must supply a config file (json) that is bound to this form")

        self._uiItems = []
        self._configFile = boundCfgFile # The file name -- use this when reading and writing the file
        self._config = None         # The dict that holds the configuration that this menu is controlling
        self._activeMenuItem = None # The active menu item (e.g. a spinner, label, button, etc.)
        self._activeSubItem = None  # The active menu item's active sub-item (e.g. a spinner's left arrow)
        self._font = None           # Font object for the form TODO - use a list? Possibly move into a FormManager class? (e.g. a FontManager could contain many forms, for multi-screen menus; and also, could manage all the font objects and what not)
        self._fontColor = None
        self._selectedItem = None

        self.loadConfigFromFile()

        if menuDefFile:
            # TODO implement this -- load menu definition from json
            # Maybe call a function to load from json?
            pass
        else:
            # TODO don't hardcode menu definition? Right now, menu is hardcoded and passed into this constructor
            pass

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

    def processMouseEvent(self, event):
        """Process mouse event

           Events are Pygame events
        """
        # TODO Make it possible for the UI to know where the "cursor" is, and to be able to move the cursor with the mouse, joystick, whatever. Also, the UI should respond to button presses on the keyboard, mouse, joystick, whatever
        # TODO update UI event handling to be more modular -- e.g. this UI form should call functions to handle a "button press" regardless of what input device generated the input
        for uiItem in self._uiItems:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousePos = pygame.mouse.get_pos()
                pressedButtons = pygame.mouse.get_pressed() # [0] = left; [1] = middle; [2] = right
                timeStamp = pygame.time.get_ticks() / 1000.0 # get timestamp; convert to seconds
                ##print "Clicked a button: {}, coord:{}, time:{}".format(pressedButtons, mousePos, timeStamp)

                # NOTE: This is the composite spinner object (the item can be contained in a list of objects or whatever)
                # TODO - form controls should be in a list/array
                # TODO add mouse-in-bounds test for label items. Even though they don't respond to mouse clicks, it might be useful (esp to make buttons, which are, essentially, labels with an action)
                if uiItem['uiItem'].isMouseWithinBounds(mousePos): 
                    ##print "Mouse click button {} on object id:{}".format(event.button, id(uiItem))
                    # TODO perhaps separate the setting of the active item (during collection phase) from the handling (e.g. setting initial timer)/update
                    # TODO send a key/button press to the object (perhaps the object can have a queue of timestamped inputs, to process and look for double-clicks, etc)
                    self._activeMenuItem = uiItem['uiItem']   # activeMenuItem is a variable that maybe can belong to a top-level UI manager object thingamajig

                    self._activeSubItem = uiItem['uiItem'].selectedSubItem(mousePos)    # activeSubItem is a variable that maybe can belong to a top-level UI manager object thingamajig
                    self._activeSubItem.setMouseButtonState(event.button - 1, menu_item_base.UIItemState.mouseButtonDown, pygame.time.get_ticks() / 1000.0)
                    if self._activeSubItem._onClickFunc:
                        ##print "Calling uiItem subItem {} _onClickFunc"
                        self._activeSubItem._onClickFunc() 
                        # Because the spinner is initialized with a bound value, which is managed internally, onClickFunc does not need to pass in any parameters
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if self._activeMenuItem:
                    # Unset whatever button was pressed (i.e. unset mouse tracking var of active menu item
                    self._activeMenuItem.setMouseButtonState(event.button - 1, menu_item_base.UIItemState.mouseButtonUp, pygame.time.get_ticks() / 1000.0)
                    # NOTE: because activeSubItem (used above) is local scope, we can't use it here. Instead, we "ask" the menu item for its subitems.
                    # TODO: fix your busted design
                    if self._activeMenuItem._subItems:
                        # NOTE: This is janky - design a better way to track the state of subItems
                        for subItem in self._activeMenuItem._subItems:
                            subItem.setMouseButtonState(event.button - 1, menu_item_base.UIItemState.mouseButtonUp, pygame.time.get_ticks() / 1000.0)

            # TODO Detect that the user clicked e.g. in menu whitespace, and set self._activeMenuItem to None
            # TODO Detect that the user clicked e.g. in menu whitespace, and set self._activeSubItem to None

    def addMenuItem(self, uiItem, kbSelectIdx=None):
        """Add a UI menu item to this form's list of UI items
        """
        # TODO -- make this a dict. Add a flag for keyboard-interactive (i.e., anything could theoretically respond to the mouse/joystick, , but we have to include info about what's interactive with the keyboard
        self._uiItems.append( {'uiItem': uiItem, 'kbSelectIdx': kbSelectIdx} )
        # kbSelectIdx tells the item how to interact with the keyboard. The index # is the number in the list of keyboard-interactive items

    def update(self, dt_s):
        """Update
        """
        #TODO (only update the active item? All items?)
        for uiItem in self._uiItems:
            uiItem['uiItem'].update(dt_s)

    def render(self, renderSurface):
        for uiItem in self._uiItems:
            uiItem['uiItem'].render(renderSurface)
