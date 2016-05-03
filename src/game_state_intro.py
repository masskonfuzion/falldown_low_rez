# Import game objects (perhaps this can go into a "game manager" of some sort?)
import pygame
import sys

from display_msg import DisplayMessage
from display_msg_manager import DisplayMessageManager
from message_queue import MessageQueue

import game_state_base
import game_state_main_menu
# NOTE: Looks like we have to use full import names, because we have circular imports (i.e. intro state imports playing state; but playing state imports intro state. Without using full import names, we run into namespace collisions and weird stuff)

class GameStateIntro(game_state_base.GameStateBase):
    __instance = None

    def __new__(cls):
        """Override the instantiation of this class. We're creating a singleton yeah"""
        return None

    def __init__(self):
        """ This shouldn't run.. We call __init__ on the __instance member"""
        pass

    def Init(self, engineRef):
		# Snag some vital object refs from the engine object
        self.game_size = engineRef.game_size
        self.screen_size = engineRef.screen_size
        self.cell_size = engineRef.cell_size
        self.surface_bg = engineRef.surface_bg
        self.game_viewport = engineRef.game_viewport
        self.bg_col = engineRef.bg_col


        self._eventQueue = MessageQueue() # Event queue, e.g. user key/button presses, system events
        self._eventQueue.Initialize(64)

        #self._cmdQueue = MessageQueue() # Command queue, e.g. "Start moving left"
        #self._cmdQueue.Initialize(64)

        # Register Event Listeners
        # Haha, psych! There are none

        # Register Command Listeners
        # Ditto

        self.mm = DisplayMessageManager()

        self.displayMsgScore = DisplayMessage()
        self.displayMsgScore.create(txtStr="Intro", position=[66, 5], color=(192,192,192))

    def Cleanup(self):
        # NOTE this class is a port from a C++ class. Because Python is garbage-collected, Cleanup() is probably not necessary here. But it's included for completeness
        pass

    @staticmethod
    def Instance():
        """Return the instance reference. Create it if it doesn't exist
           
           This method is a static method because it does not use any object
        """
        if GameStateIntro.__instance is None:
            GameStateIntro.__instance = super(GameStateIntro, GameStateIntro).__new__(GameStateIntro)
            GameStateIntro.__instance.__init__()
            GameStateIntro.__instance.SetName("Intro State")
        return GameStateIntro.__instance
        

    # TODO Consider changing "pause" to "PushState" or something; doesn't HAVE to be 'pause'
    def Pause(self):
        # TODO check your design - you may need a pointer/reference to the engine here, to be able to push onto the stack.
        print "GAMESTATE Intro State pausing"

    # TODO Consider changing "resume" to "PopState" or something; doesn't HAVE to be 'resume'
    def Resume(self):
        # TODO check your design - you may need a pointer/reference to the engine here, to be able to pop from the stack
        print "GAMESTATE Intro State resume"

    def ProcessEvents(self, engineRef):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # TODO Create a quit request message, and add it to the Messaging Handler. Oh yeah, also make a Messaging Handler
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                    engineRef.changeState(game_state_main_menu.GameStateMainMenu.Instance())

    def ProcessCommands(self, engineRef):
        # No command processing needed here because this is a super-simple pause state
        # However, in a more complex game, the pause menu could have more intricate controls and elements (e.g. settings menu or something), in which case command processing could be needed
        pass


    def Update(self, engineRef, dt_s, cell_size):
        # No updates needed here
        pass

    def PreRenderScene(self, engineRef):
        pass

    def RenderScene(self, engineRef):
        self.surface_bg.fill((0,0,0))
        self.game_viewport.fill(self.bg_col)
        

    def PostRenderScene(self, engineRef):
        self.displayGameStats()
        self.surface_bg.blit(self.game_viewport, (0, 0))    # blit the game viewport onto the bigger surface_bg
        pygame.display.flip()


    def displayGameStats(self):
        # Janky hardcoding here... TODO fix the jankiness
        self.displayMsgScore.changeText("Intro")
        textSurfaceScore = self.displayMsgScore.getTextSurface(self.mm._font)
        self.surface_bg.blit(textSurfaceScore, (self.displayMsgScore._position[0] * self.cell_size[0], self.displayMsgScore._position[1] * self.cell_size[1] ))

