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

import pygame
import sys
import os
import sound_and_music

class GameApplication(object):
    ''' Application class that stores all the data and stuff
    '''
    def __init__(self):
        ''' Application class
        '''
        # TODO make screen size customizable. Use the dot-access config dict structure

        # dirt-nasty initialization: screen_size is a tuple (width, height); width, height is initialized as 640x640
        self.game_size = [640, 640]
        self.screen_size = [854, 640] # The playable area will be a 640 x 640 square.
        self.cell_size = [self.game_size[0] / 64, self.game_size[1] / 64] # cell size (starts off as 10px x 10px. recompute this if screen size changes)
        #self.surface_bg = pygame.display.set_mode(self.screen_size)
        self.surface_bg = pygame.display.set_mode(self.screen_size, pygame.DOUBLEBUF, 32)
        self.game_viewport = pygame.Surface((640, 640))
        self.mixer = sound_and_music.SoundNMusicMixer()
        self.exepath = os.path.dirname(sys.argv[0])     # Get the path where the script is. This allows us to properly compute relative paths to assets, e.g. images, sounds, etc.

        self.bg_col = 255,255,255
        self.isRunning = True
        self._states = []   # States are managed via stack, which we will implement using a Python list

    def cleanup(self):
        pass

    def setRunningFlagToFalse(self, argsDict = None):
        """Set the application's isRunning flag to alse

           Note: argsDict is in the function header to accommodate EventQueue/Messaging system design. Those systems procedurally generate a function call that expects an arguments dict.
        """
        print "Thank you for playing Falldown :-)"
        self.isRunning = False

    def changeState(self, toState, takeWith=None):
        """Change State to toState

           takeWith is an object (likely a list or dict) of objects to transfer into to the toState
        """
        fromState = self.popState() # Get the current state and then pop it off the stack
        if fromState:
            fromState.Cleanup()

        self.pushState(toState, takeWith)

    def getState(self):
        """Return a reference to the state at the top of the stack"""
        if self._states:
            return self._states[ len(self._states) - 1 ]
        else:
            return None

    def pushState(self, toState, takeWith=None):
        """Push toState onto the stack"""
        self._states.append(toState)
        self.getState().Init(self, takeWith)

    def popState(self):
        """Remove state from the stack, and return it"""
        fromState = None
        if self._states:
            fromState = self._states.pop()
        return fromState

    def update(self, dt_s, cell_size):
        """Call Update() on state at top of stack
           
           Call State's Update(), passing in a reference to the engine. The state may need a reference to the engine, especially when the engine has valuable data, e.g. time keeping or other objects the state needs access to
        """
        self.getState().Update(self, dt_s, cell_size)

    def processEvents(self):
        """Call ProcessEvents on state at top of stack"""
        self.getState().ProcessEvents(self)

    def processCommands(self):
        """Call ProcessEvents on state at top of stack"""
        self.getState().ProcessCommands(self)

    def preRenderScene(self):
        """Call PreRender on state at top of stack"""
        self.getState().PreRenderScene(self)

    def renderScene(self):
        ''' Render scene
            NOTE render() does not 'write' to the screen.
        '''
        """Call PreRender on state at top of stack"""
        # Draw all states on the stack (this allows for one state to overlay on another, e.g. a pause menu overlaid on the game playing screen))
        for state in self._states:
            state.RenderScene(self)

    def postRenderScene(self):
        """Call PreRender on state at top of stack"""
        self.getState().PostRenderScene(self)
