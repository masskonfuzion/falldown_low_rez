import pygame
from gameobj import GameObj

class DisplayMessage(GameObj):
    def __init__(self):
        super(DisplayMessage, self).__init__()
        self._text = ""
        self._ttl = 3.0
        self._age = 0.0
        self._alive = False
        self._color = (128, 128, 0)

    def create(self, txtStr="", position=[0,0], color=(128, 128, 0), ttl=3):
        self._text = txtStr
        self._color = color
        self.setPosition( position[0], position[1] )
        self._ttl = ttl
        self._age = 0.0
        self._alive = True

    def update(self, dt_s, cell_size):
        if not self._alive:
            return

        self._age += dt_s
        if self._age > self._ttl:
            self._alive = False


    def getTextSurface(self, fontObj):
        ''' Return a pygame text surface object. To render on-screen, the game must blit the surface to the screen
            The font object will be supplied by the DisplayMessageManager that manages this text
        '''
        # Could use sexy Python "a if c else b" ternary here; but whatever :-)
        retObj = None
        if self._alive:
            retObj = fontObj.render(self._text, True, self._color)

        return retObj


