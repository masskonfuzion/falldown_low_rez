import random
import pygame
from gameobj import GameObj
from collision_aabb import CollisionAABB


# TODO add a CollisionAABB to the row. And, for that matter to the ball

class Row(GameObj):
    ''' A row of blocks.
    '''

    def __init__(self, numBlocks = 16, yPosition = 32, gap = -1):
        super(Row, self).__init__()

        self._numBlocks = numBlocks # Prefer this number to be a factor of 64
        self._position[1] = yPosition # We really only care about the row's y position on the grid (x defaults to 0)
        self._drawRects = [None, None]
        self._collGeoms = [None, None]
        self._blockWidth = 64 / self._numBlocks # block width in terms of grid cells
        self._blockHeight = 2

        self.setGap(gap)

        self.setSize(64 / self._numBlocks, 2) # NOTE: Size here is PER BLOCK, in terms of grid cells. (TODO: You can probably delete blockWidth and blockHeight


    def draw(self, screen, cell_size):
        for rect in self._drawRects:
            if rect:
                pygame.draw.rect(screen, (128, 128, 128), rect)

        # DEBUG draw the collision geometry
        for geom in self._collGeoms:
            if geom:
                geom.draw(screen, cell_size)


    def _getRandomGap(self):
        return random.randint(0, self._numBlocks - 1)


    def setGap(self, gap):
        self._gap = self._getRandomGap() if gap == -1 else gap
        #TODO Consider computing render geometry here? And also collision geometry? (If we're using collision geometry)

    def getGap(self):
        return self._gap


    def update(self, dt_s, cell_size):
        # TODO: Uhm, actually move the rows

        # Upon movement, recompute render and collision geometry
        # TODO: Fix - you're creating a totally new collision geom on every update.. That's wasteful. Instead, create the collision geom at the same time as the row is created
        self._computeRenderGeometry(cell_size)
        self._computeCollisionGeometry(cell_size)

    def _computeRenderGeometry(self, cell_size):
        if self._gap == 0:
            # Draw 1 row section
            sPt = [ (self._gap + 1) * self._size[0] * cell_size[0], self._position[1] * cell_size[1] ]
            ePt = [ sPt[0] + 63 * cell_size[0], sPt[1] + self._size[1] * cell_size[1] ]

            self._drawRects[0] = (sPt[0], sPt[1], ePt[0] - sPt[0], ePt[1] - sPt[1]) # Rects are defined as (left, top, width, height)

        elif self._gap == self._numBlocks - 1:
            # Draw 1 row section
            sPt = [ 0, self._position[1] * cell_size[1] ]
            ePt = [ sPt[0] + self._gap * self._size[0] * cell_size[0], sPt[1] + self._size[1] * cell_size[1] ]

            self._drawRects[0] = (sPt[0], sPt[1], ePt[0] - sPt[0], ePt[1] - sPt[1]) # Rects are defined as (left, top, width, height)
        else:
            # Draw 2 row sections
            sPt = [ 0, self._position[1] * cell_size[1] ]
            ePt = [ sPt[0] + self._gap * self._size[0] * cell_size[0], sPt[1] + self._size[1] * cell_size[1] ]
            self._drawRects[0] = (sPt[0], sPt[1], ePt[0] - sPt[0], ePt[1] - sPt[1]) # Rects are defined as (left, top, width, height)

            sPt = [ (self._gap + 1) * self._size[0] * cell_size[0], self._position[1] * cell_size[1] ]
            ePt = [ sPt[0] + (64 - (self._gap + 1) * self._size[0]) * cell_size[0], sPt[1] + self._size[1] * cell_size[1] ]
            self._drawRects[1] = (sPt[0], sPt[1], ePt[0] - sPt[0], ePt[1] - sPt[1]) # Rects are defined as (left, top, width, height)

    def _computeCollisionGeometry(self, cell_size):
        # NOTE: In this game, the AABB geometry is the same as the rendering geometry

        # TODO: Fix calculation of position. Y is good, but X is meaningless at the moment..
        if self._gap == 0 or self._gap == self._numBlocks - 1:
            self._collGeoms[0] = CollisionAABB()
            #self._collGeoms[0].setPosition(self._position[0], self._position[1])

            # NOTE: Here, we're totally cheating and computing the AABB based on the render geometry.
            # Note rect[0] = left; rect[1] = top; rect[2] = width; rect[3] = height
            self._collGeoms[0]._minPt = [ self._drawRects[0][0], self._drawRects[0][1] ]
            self._collGeoms[0]._maxPt = [ self._drawRects[0][0] + self._drawRects[0][2], self._drawRects[0][1] + self._drawRects[0][3] ]
            self._collGeoms[0].setPosition(self._getGridCoordFromScreenCoord(self._collGeoms[0]._minPt[0], cell_size), self._position[1])
            self._collGeoms[0].setSize(self._drawRects[0][2] / cell_size[0], self._size[1])

        else:
            # Note: You ALWAYS will have at least 1 collision geom, so the if/else conditions could be different. But whatever.. :-D
            self._collGeoms[0] = CollisionAABB()
            self._collGeoms[1] = CollisionAABB()

            self._collGeoms[0]._minPt = [ self._drawRects[0][0], self._drawRects[0][1] ]
            self._collGeoms[0]._maxPt = [ self._drawRects[0][0] + self._drawRects[0][2], self._drawRects[0][1] + self._drawRects[0][3] ]
            self._collGeoms[0].setPosition(self._getGridCoordFromScreenCoord(self._collGeoms[0]._minPt[0], cell_size), self._position[1])
            self._collGeoms[0].setSize(self._drawRects[0][2] / cell_size[0], self._size[1])

            self._collGeoms[1]._minPt = [ self._drawRects[1][0], self._drawRects[1][1] ]
            self._collGeoms[1]._maxPt = [ self._drawRects[1][0] + self._drawRects[1][2], self._drawRects[1][1] + self._drawRects[1][3] ]
            self._collGeoms[1].setPosition(self._getGridCoordFromScreenCoord(self._collGeoms[1]._minPt[0], cell_size), self._position[1])
            self._collGeoms[1].setSize(self._drawRects[1][2] / cell_size[0], self._size[1])

    def _getGridCoordFromScreenCoord(self, coord, cell_size):
        return coord / cell_size[0] # Cells are square, so it doesn't matter which cell_size coordinate we use
