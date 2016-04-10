import random
import pygame
from gameobj import GameObj

class Row(GameObj):
    ''' A row of blocks.
    '''

    def __init__(self, numBlocks = 16, yPosition = 32, gap = -1):
        super(Row, self).__init__()

        self._numBlocks = numBlocks # Prefer this number to be a factor of 64
            
        self._position[1] = yPosition # We really only care about the row's y position on the grid (x defaults to 0)

        self._gap = self._getRandomGap() if gap == -1 else gap

        self._blockWidth = 64 / self._numBlocks # block width in terms of grid cells
        self._blockHeight = 2

        self.setSize(64 / self._numBlocks, 2) # NOTE: Size here is PER BLOCK, in terms of grid cells. (TODO: You can probably delete blockWidth and blockHeight


    def draw(self, screen, cell_size):
        drawRects = [None, None]
        
        if self._gap == 0:
            # Draw 1 row section
            sPt = [ (self._gap + 1) * self._size[0] * cell_size[0], self._position[1] * cell_size[1] ]
            ePt = [ sPt[0] + 63 * cell_size[0], sPt[1] + self._size[1] * cell_size[1] ]

            drawRects[0] = (sPt[0], sPt[1], ePt[0] - sPt[0], ePt[1] - sPt[1]) # Rects are defined as (left, top, width, height)
        elif self._gap == self._numBlocks - 1:
            # Draw 1 row section
            sPt = [ 0, self._position[1] * cell_size[1] ]
            ePt = [ sPt[0] + self._gap * self._size[0] * cell_size[0], sPt[1] + self._size[1] * cell_size[1] ]

            drawRects[0] = (sPt[0], sPt[1], ePt[0] - sPt[0], ePt[1] - sPt[1]) # Rects are defined as (left, top, width, height)
        else:
            # Draw 2 row sections
            sPt = [ 0, self._position[1] * cell_size[1] ]
            ePt = [ sPt[0] + self._gap * self._size[0] * cell_size[0], sPt[1] + self._size[1] * cell_size[1] ]
            drawRects[0] = (sPt[0], sPt[1], ePt[0] - sPt[0], ePt[1] - sPt[1]) # Rects are defined as (left, top, width, height)

            sPt = [ (self._gap + 1) * self._size[0] * cell_size[0], self._position[1] * cell_size[1] ]
            ePt = [ sPt[0] + (64 - (self._gap + 1) * self._size[0]) * cell_size[0], sPt[1] + self._size[1] * cell_size[1] ]
            drawRects[1] = (sPt[0], sPt[1], ePt[0] - sPt[0], ePt[1] - sPt[1]) # Rects are defined as (left, top, width, height)

        for rect in drawRects:
            if rect:
                pygame.draw.rect(screen, (128, 128, 128), rect)


    def _getRandomGap(self):
        return random.randint(0, self._numBlocks - 1)


    def setGap(self, gap):
        self._gap = gap
        #TODO Consider computing render geometry here? And also collision geometry? (If we're using collision geometry)

    def getGap(self):
        return self._gap
