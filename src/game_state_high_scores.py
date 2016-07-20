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
import menu_item_textbox
#import menu_item_spinner

import game_state_base
import game_state_main_menu
# NOTE: Looks like we have to use full import names, because we have circular imports (i.e. intro state imports playing state; but playing state imports intro state. Without using full import names, we run into namespace collisions and weird stuff)

import sound_and_music

class GameStateImpl(game_state_base.GameStateBase):
    __instance = None

    def __new__(cls):
        """Override the instantiation of this class. We're creating a singleton yeah"""
        return None

    def __init__(self):
        """ This shouldn't run.. We call __init__ on the __instance member"""
        pass

    def Init(self, engineRef, takeWith=None):
        #print "{} state Init()".format(self._name)

		# Snag some vital object refs from the engine object
        self.game_size = engineRef.game_size
        self.screen_size = engineRef.screen_size
        self.cell_size = engineRef.cell_size
        self.surface_bg = engineRef.surface_bg
        self.bg_col = engineRef.bg_col
        self.mixer = engineRef.mixer

        self._eventQueue = MessageQueue() # Event queue, e.g. user key/button presses, system events
        self._eventQueue.Initialize(16)

        # TODO Pick up from here: Model this UI after the settings state
        self.ui = menu_form.UIForm('../data/scores/highscores.json', engineRef=engineRef) # the LHS engineRef is the function param; the RHS engineRef is the object we're passing in
        # TODO -- figure out why the "Loaded high scores" message popeed up twice. It seems as though the changeState() function call is being done twice?
        #print "Loaded high scores:\n{}".format(self.ui._boundObj)
        self.ui._font = menu_form.UIForm.createFontObject('../asset/font/ARCADE.TTF', 32)

        # TODO The high scores display should either use labels (which are read-only, and which means you need to bind the label text value to a config item); or, you can lock the form so that the read/write textboxes are temporarily read-only when _viewing_ the high scores, but _read/write_ when the player achieves a high score.

        # NOTE: The high scores file has strings with numeric values, because Python (or maybe the json module, or maybe the dot access dict) tripped over loading int values of 0 from the file. I don't know..
        for i in range(0,10):
            self.ui.addMenuItem( menu_item_label.MenuItemLabel([50,80 + 40*i], self.ui._font, '{}.'.format(str(i+1))), kbSelectIdx=None )
            ##print "Adding UI item keyed to {}, value: {}".format('{}.name'.format(str(i)), self.ui._boundObj['{}.name'.format(str(i))])
            # Note: Here we're hacking a textbox to behave like a label. TODO get rid of the label item? (It's redundant with a locked textbox)
            self.ui.addMenuItem( menu_item_textbox.MenuItemTextbox(self.ui._boundObj, '{}.name'.format(str(i)), [100,80 + 40*i], self.ui._font, locked=True), kbSelectIdx=None )
            ##print "Adding UI item keyed to {}, value: {}".format('{}.score'.format(str(i)), self.ui._boundObj['{}.score'.format(str(i))])
            self.ui.addMenuItem( menu_item_textbox.MenuItemTextbox(self.ui._boundObj, '{}.score'.format(str(i)), [600,80 + 40*i], self.ui._font, locked=True), kbSelectIdx=None )

        self.ui.addMenuItem( menu_item_label.MenuItemLabel([300, 500], self.ui._font, 'Return'), kbSelectIdx=0, action="exitUI" )

        self.ui._kbSelection = 0 # It is necessary to set the selected item (the keyboard selection) manually. Otherwise, the UI has no way of knowing which item to interact with
        self.ui._maxKbSelection = 0 # Janky hack to know how many kb-interactive items are on the form # TODO is there a better way to specify maximum? Or maybe write an algo that figures this out?

        #Adding another DisplayMessageManager for the Title text. This is a bit hacky..
        self.title_mm = DisplayMessageManager()
        self.title_mm._font = pygame.font.Font('../asset/font/ARCADE.TTF', 64)

        self.titleMsg = DisplayMessage()
        self.titleMsg.create(txtStr='High Scores', position=[1,1], color=(192,192,192))

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
            GameStateImpl.__instance.SetName("HighScores State")
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
        #print "game_state_high_scores: Enqueued action={} into command queue".format(action)
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
            if argsDict['uiCommand'] == 'exitUI':
                engineRef.changeState(game_state_main_menu.GameStateImpl.Instance())

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
                # TODO add some logic here to determine what key the user hit. If the user has an active textbox, then alphanumeric keypresses should register as editing the textbox contents; enter confirms; shift + arrows/home/end highlights text (fancy), or otherwise some key (maybe ctrl + something) clear the textbox; etc.
                #print "game_state_high_scores: User pressed key. Event = {}".format(event)
                action = self.ui.processKeyboardEvent(event, engineRef)

                if action:
                    #print "game_state_high_scores: UI returned action: {}. Enqueueing into command queue".format(action)
                    self.EnqueueUICommandMessage(action)

            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                action = self.ui.processMouseEvent(event, engineRef)

                if action:
                    self.EnqueueUICommandMessage(action)

            elif event.type == sound_and_music.SoundNMusicMixer.SONG_END_EVENT:
                self.mixer.loadMusicFile('Theme')
                self.mixer.playMusic()  # No matter what song was playing, load up the theme song next and play it
                                        # TODO add config options for music on/off; obey those settings.

    def ProcessCommands(self, engineRef):
        msg = self._eventQueue.Dequeue()
        while msg:
            #print "DEBUG Dequeued message: {}".format(msg)
            topic = msg['topic']
            for listener_obj_dict in self._eventQueue.RegisteredListeners(topic):
                #print "game_state_high_scores: Registered Listener {} processing message {}".format(listener_obj_dict['name'], msg['payload'])

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
        self.ui.update(dt_s)

    def PreRenderScene(self, engineRef):
        pass

    def RenderScene(self, engineRef):
        self.surface_bg.fill((0,0,0))

        self.ui.render(self.surface_bg)

        textSurf = self.titleMsg.getTextSurface(self.title_mm._font)
        self.surface_bg.blit(textSurf, (self.titleMsg._position[0] * self.cell_size[0], self.titleMsg._position[1] * self.cell_size[1]))
        

    def PostRenderScene(self, engineRef):
        # Draw a box around the selected menu item
        # NOTE: I could've put the box in the renderScene function, but the box is technically an "overlay". Also, whatever, who cares? :-D

        ## # TODO perhaps make a function in the menuform class that draws the selection (and make it customizable?)

        # Flip the buffers
        pygame.display.flip()


