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

class GameStateImpl(game_state_base.GameStateBase):
    __instance = None

    def __new__(cls):
        """Override the instantiation of this class. We're creating a singleton yeah"""
        return None

    def __init__(self):
        """ This shouldn't run.. We call __init__ on the __instance member"""
        pass

    def Init(self, engineRef, takeWith=None):
		# Snag some vital object refs from the engine object
        self.game_size = engineRef.game_size
        self.screen_size = engineRef.screen_size
        self.cell_size = engineRef.cell_size
        self.surface_bg = engineRef.surface_bg          # Possibly won't use this surface for the pause menu. We want to overlay our own surface on top of this one
        self.game_viewport = engineRef.game_viewport    # Possibly won't use this surface for the pause menu. We want to overlay our own surface on top of this one
        self.bg_col = engineRef.bg_col
        self.mixer = engineRef.mixer

        self.surface_overlay = pygame.Surface((640, 480))
        #self.surface_overlay.set_colorkey((64,64,64))   # NOTE: To get a transparency effect, this colorkey value has to be the same as the fill color used during rendering this surface
        self.surface_overlay.set_colorkey((0,0,0))   # NOTE: To get a transparency effect, this colorkey value has to be the same as the fill color used during rendering this surface

        self.blit_center = ( self.surface_bg.get_size()[0] / 2 - self.surface_overlay.get_size()[0] / 2, self.surface_bg.get_size()[1] / 2 - self.surface_overlay.get_size()[1] / 2 )

        self._eventQueue = MessageQueue() # Event queue, e.g. user key/button presses, system events
        self._eventQueue.Initialize(16)

        # TODO remove self.mm and self.displayMsgScore (which doesn't hold the score.. That's an artifact of copy/paste rushing when trying to submit to low-rez-jam
        self.mm = DisplayMessageManager()

        self.displayMsgScore = DisplayMessage()
        self.displayMsgScore.create(txtStr="Pause", position=[66, 5], color=(192,192,192))

        # TODO Allow customization of text colors in the UI
        self.ui = menu_form.UIForm(engineRef=engineRef) # the LHS engineRef is the function param; the RHS engineRef is the object we're passing in
        self.ui._font = menu_form.UIForm.createFontObject('../asset/font/ARCADE.TTF', 32)   # TODO maybe load one font obj at a higher-level scope than any menu or game state; then pass it in, instead of constructing one at each state change
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([200, 200], self.ui._font, 'Paused'), kbSelectIdx=None )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([200, 250], self.ui._font, 'Resume Game'), kbSelectIdx=0, action="resumeGame" )
        self.ui.addMenuItem( menu_item_label.MenuItemLabel([200, 300], self.ui._font, 'Back to Main Menu'), kbSelectIdx=1, action="exitUI" )

        self.ui._kbSelection = 0 # It is necessary to set the selected item (the keyboard selection) manually. Otherwise, the UI has no way of knowing which item to interact with
        self.ui._maxKbSelection = 1 # Janky hack to know how many kb-interactive items are on the form # TODO is there a better way to specify maximum? Or maybe write an algo that figures this out?

        # Register Event Listeners
        self._eventQueue.RegisterListener('self', self, 'UIControl')    # Register "myself" as an event listener

    def Cleanup(self):
        # NOTE this class is a port from a C++ class. Because Python is garbage-collected, Cleanup() is probably not necessary here. But it's included for completeness
        pass

    @staticmethod
    def Instance():
        """Return the instance reference. Create it if it doesn't exist
           
           This method is a static method because it does not use any object
        """
        if GameStateImpl.__instance is None:
            GameStateImpl.__instance = super(GameStateImpl, GameStateImpl).__new__(GameStateImpl)
            GameStateImpl.__instance.__init__()
            GameStateImpl.__instance.SetName("Pause State")
        return GameStateImpl.__instance
        

    # TODO Consider changing "pause" to "PushState" or something; doesn't HAVE to be 'pause'
    def Pause(self):
        pass

    # TODO Consider changing "resume" to "PopState" or something; doesn't HAVE to be 'resume'
    def Resume(self):
        pass

    def EnqueueUICommandMessage(self, action):
        """Enqueue a UI command message for handling

           # NOTE: Every message must have an 'action' key/val. The message parser will look for the 'action' in order to know what to do
        """
        self._eventQueue.Enqueue( { 'topic': 'UIControl',
                                    'payload': { 'action': 'call_function'
                                               , 'function_name': 'DoUICommand'
                                               , 'params' : 'uiCommand="{}"'.format(action)
                                               }
                                  } ) # here, the call keyword says that the message payload is an instruction to call a function

    def DoUICommand(self, engineRef, argsDict):
        """
           NOTE: This function assumes argsDict has one key only: uiCommand. The value of that key dictates what to do
        """
        # TODO process the args and figure out what to do
        try:
            if argsDict['uiCommand'] == 'resumeGame':
                engineRef.getState().Cleanup()
                engineRef.popState() # NOTE: PopState() returns the state to the program; however, we don't assign it, because we don't care, because we're not going to use it for anything
            elif argsDict['uiCommand'] == 'exitUI':
                engineRef.changeState( game_state_main_menu.GameStateImpl.Instance() )
        except KeyError as e:
            # if there is no uiCommand defined, don't do anything
            # (could have also tested if argsDict['uiCommand'] exists, without exception handling, but I like the way the code looks here)
            pass

    def ProcessEvents(self, engineRef):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # TODO Create a quit request message, and add it to the Messaging Handler. Oh yeah, also make a Messaging Handler
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # TODO Perhaps add to the UI a way to determine what the "action activator buttons" should be. e.g., some menus should respond to ESC key, others only ENTER, SPACE, etc. The pause menu should respond to "p"
                action = self.ui.processKeyboardEvent(event, engineRef)
                if action:
                    self.EnqueueUICommandMessage(action)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                action = self.ui.processMouseEvent(event, engineRef)
                if action:
                    self.EnqueueUICommandMessage(action)

    def ProcessCommands(self, engineRef):
        msg = self._eventQueue.Dequeue()
        while msg:
            #print "DEBUG Dequeued message: {}".format(msg)
            topic = msg['topic']
            for listener_obj_dict in self._eventQueue.RegisteredListeners(topic):
                #print "DEBUG Registered Listener {} processing message {}".format(listener_obj_dict['name'], msg['payload'])

                # Evaluate the 'action' key to know what to do. The action dictates what other information is required to be in the message
                if msg['payload']['action'] == 'call_function':
                    # The registered listener had better have the function call available heh... otherwise, kaboom
                    objRef = listener_obj_dict['ref']
                    fn_ptr = getattr(objRef, msg['payload']['function_name'])

                    argsDict = eval("dict({})".format(msg['payload']['params']))

                    # NOTE: Slight cheat here: because this menu is its own event listener, and it's the only one, we pass in engineRef (the application object reference), instead of passing self (as we do in other game states). fn_ptr already points to self.DoUICommand. Admittedly, this is probably over-complicated, but it works..
                    fn_ptr(engineRef, argsDict)

            msg = self._eventQueue.Dequeue()

    def Update(self, engineRef, dt_s, cell_size):
        # No updates needed here
        pass

    def PreRenderScene(self, engineRef):
        pass

    def RenderScene(self, engineRef):
        #self.surface_bg.fill((0,0,0))          # I think we want to NOT fill, so we can overlay.
        #self.game_viewport.fill(self.bg_col)
        self.surface_overlay.fill((0,0,0))  # This is one way to do transparency...: above, the colorkey for this surface is (0,0,0). That causes Pygame to NOT blit any pixels colored (0,0,0), thus causing anything NOT colored (0,0,0) on this surface to not be rendered, making this surface look transparent.
        
        # Render the UI
        self.ui.render(self.surface_overlay)

    def PostRenderScene(self, engineRef):
        #self.displayGameStats() # TODO remove this jank. There are no game stats to display in the pause state (or, otherwise, display the actual game stats: # of tries, level, etc)

        self.game_viewport.blit(self.surface_overlay, self.blit_center)
        self.surface_bg.blit(self.game_viewport, (0, 0))
        pygame.display.flip()


    def displayGameStats(self):
        # Janky hardcoding here... TODO fix the jankiness
        self.displayMsgScore.changeText("Pause")
        textSurfaceScore = self.displayMsgScore.getTextSurface(self.mm._font)
        self.surface_bg.blit(textSurfaceScore, (self.displayMsgScore._position[0] * self.cell_size[0], self.displayMsgScore._position[1] * self.cell_size[1] ))

