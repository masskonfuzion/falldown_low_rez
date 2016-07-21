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

import random
import pygame
from gameobj import GameObj
from collision_aabb import CollisionAABB


class Row(GameObj):
    # Define some static vars that we'll use to initialize the collision geoms - types should be non-zero, because the CollisionAABB class initializes to 0
    COLLISION_TYPE_NONE = 0
    COLLISION_TYPE_ROW = 1
    COLLISION_TYPE_GAP = 2
    ''' A row of blocks.
    '''
    def __init__(self, numBlocks = 16, yPosition = 32, gap = -1, updateDelay = 1):
        super(Row, self).__init__()

        self._numBlocks = numBlocks # Prefer this number to be a factor of 64
        self._position[1] = yPosition # We really only care about the row's y position on the grid (x defaults to 0)
        self._drawRects = [None, None]
        self._collGeoms = [None, None, None] # geom[0] is the gap (used for scorekeeping), geom[1] is row block 1, geom[2] is row block 2 (if applicable)

        self.setGap(gap)

        self._updateDelay = 0.0
        self.setUpdateDelay(updateDelay) # Update delay in seconds

        self.setSize(64 / self._numBlocks, 2) # NOTE: Size here is PER BLOCK, in terms of grid cells.


    def draw(self, screen, cell_size):
        for rect in self._drawRects:
            if rect:
                pygame.draw.rect(screen, (128, 128, 128), rect)

        ## DEBUG draw the collision geometry
        #for geom in self._collGeoms:
        #    if geom:
        #        geom.draw(screen, cell_size)


    def _getRandomGap(self):
        return random.randint(0, self._numBlocks - 1)


    def setGap(self, gap):
        self._gap = self._getRandomGap() if gap == -1 else gap


    def getGap(self):
        return self._gap


    def setUpdateDelay(self, delay_s):
        self._updateDelay = delay_s


    def reInit(self, cell_size, yPosition = 32, gap = -1, game_stats_obj = None):
        self._position[1] = yPosition # We really only care about the row's y position on the grid (x defaults to 0)
        self.setGap(gap)

        # Create new Render and Collision geoms (can't simply modify existing ones, because the gap can change (which changes the necessary geom references)
        self._createRenderGeometry(cell_size)
        self._createCollisionGeometry(cell_size)

    def update(self, dt_s, cell_size, game_stats_obj):
        self._position[1] -= 1

        # Upon movement, recompute render and collision geometry
        # TODO: Fix - you're creating a totally new collision geom on every update.. That's wasteful. Instead, create the collision geom at the same time as the row is created, and simply move it on update
        self._updateRenderGeometry(cell_size)
        self._updateCollisionGeometry(cell_size)


    def _createRenderGeometry(self, cell_size):
        if self._gap == 0:
            # Draw 1 row section
            sPt = [ (self._gap + 1) * self._size[0] * cell_size[0], self._position[1] * cell_size[1] ]
            ePt = [ sPt[0] + 63 * cell_size[0], sPt[1] + self._size[1] * cell_size[1] ]

            self._drawRects[0] = pygame.Rect(sPt[0], sPt[1], ePt[0] - sPt[0], ePt[1] - sPt[1]) # Rects are defined as (left, top, width, height)

        elif self._gap == self._numBlocks - 1:
            # Draw 1 row section
            sPt = [ 0, self._position[1] * cell_size[1] ]
            ePt = [ sPt[0] + self._gap * self._size[0] * cell_size[0], sPt[1] + self._size[1] * cell_size[1] ]

            self._drawRects[0] = pygame.Rect(sPt[0], sPt[1], ePt[0] - sPt[0], ePt[1] - sPt[1]) # Rects are defined as (left, top, width, height)
        else:
            # Draw 2 row sections
            sPt = [ 0, self._position[1] * cell_size[1] ]
            ePt = [ sPt[0] + self._gap * self._size[0] * cell_size[0], sPt[1] + self._size[1] * cell_size[1] ]
            self._drawRects[0] = pygame.Rect(sPt[0], sPt[1], ePt[0] - sPt[0], ePt[1] - sPt[1]) # Rects are defined as (left, top, width, height)

            sPt = [ (self._gap + 1) * self._size[0] * cell_size[0], self._position[1] * cell_size[1] ]
            ePt = [ sPt[0] + (64 - (self._gap + 1) * self._size[0]) * cell_size[0], sPt[1] + self._size[1] * cell_size[1] ]
            self._drawRects[1] = pygame.Rect(sPt[0], sPt[1], ePt[0] - sPt[0], ePt[1] - sPt[1]) # Rects are defined as (left, top, width, height)


    def _createCollisionGeometry(self, cell_size):
        # NOTE: In this game, the AABB geometry is the same as the rendering geometry

        # NOTE: We make sure to put the gap in slot 0, so we can test for collisions with the ball against the gap 1st, before the row geoms

        # TODO Don't create new CollisionAABB's at every recomputation.. That stresses the garbage collector. Just reinitialize existing geoms. For geom[2], which may or may not be active, set to COLLISION_TYPE_NONE to tell game not to use it for anything

        # Also Note: You could have computed the collision geom based on the render geometry, but multiplying things is more fun
        self._collGeoms[0] = CollisionAABB()
        self._collGeoms[0]._type = Row.COLLISION_TYPE_GAP
        offset = 0 # Grid offset to put collision 'zone' for score keeping
        self._collGeoms[0]._minPt = [ (self._gap * self._size[0] * cell_size[0]) + cell_size[0], (self._position[1]) * cell_size[1] ]
        self._collGeoms[0]._maxPt = [ (self._gap * self._size[0] * cell_size[0]) + (self._size[0] - 1) * cell_size[0], (self._position[1] + self._size[1] + offset) * cell_size[1] ]
        self._collGeoms[0].setPosition(self._getGridCoordFromScreenCoord(self._collGeoms[0]._minPt[0], cell_size), self._position[1] + self._size[1] + offset)
        self._collGeoms[0].setSize((self._collGeoms[0]._maxPt[0] - self._collGeoms[0]._minPt[0]) / cell_size[0], 1)
        #print "Gap: type:{} minPt:{} maxPt:{} pos:{} size:{}".format(self._collGeoms[0]._type, self._collGeoms[0]._minPt, self._collGeoms[0]._maxPt, self._collGeoms[0]._position, self._collGeoms[0]._size)

        if self._gap == 0 or self._gap == self._numBlocks - 1:
            self._collGeoms[1] = CollisionAABB()
            self._collGeoms[2] = None
            #self._collGeoms[0].setPosition(self._position[0], self._position[1])

            # NOTE: Here, we're totally cheating and computing the AABB based on the render geometry.
            # Note rect[0] = left; rect[1] = top; rect[2] = width; rect[3] = height
            self._collGeoms[1]._type = Row.COLLISION_TYPE_ROW
            self._collGeoms[1]._minPt = [ self._drawRects[0][0], self._drawRects[0][1] ]
            self._collGeoms[1]._maxPt = [ self._drawRects[0][0] + self._drawRects[0][2], self._drawRects[0][1] + self._drawRects[0][3] ]
            self._collGeoms[1].setPosition(self._getGridCoordFromScreenCoord(self._collGeoms[1]._minPt[0], cell_size), self._position[1])
            self._collGeoms[1].setSize(self._drawRects[0][2] / cell_size[0], self._size[1])
            #print "Row: type:{} minPt:{} maxPt:{} pos:{} size:{}".format(self._collGeoms[1]._type, self._collGeoms[1]._minPt, self._collGeoms[1]._maxPt, self._collGeoms[1]._position, self._collGeoms[1]._size)

        else:
            # Note: You ALWAYS will have at least 2 collision geom, so the if/else conditions could be different. But whatever.. :-D
            self._collGeoms[1] = CollisionAABB()
            self._collGeoms[2] = CollisionAABB()

            self._collGeoms[1]._type = Row.COLLISION_TYPE_ROW
            self._collGeoms[1]._minPt = [ self._drawRects[0][0], self._drawRects[0][1] ]
            self._collGeoms[1]._maxPt = [ self._drawRects[0][0] + self._drawRects[0][2], self._drawRects[0][1] + self._drawRects[0][3] ]
            self._collGeoms[1].setPosition(self._getGridCoordFromScreenCoord(self._collGeoms[1]._minPt[0], cell_size), self._position[1])
            self._collGeoms[1].setSize(self._drawRects[0][2] / cell_size[0], self._size[1])
            #print "Row: type:{} minPt:{} maxPt:{} pos:{} size:{}".format(self._collGeoms[1]._type, self._collGeoms[1]._minPt, self._collGeoms[1]._maxPt, self._collGeoms[1]._position, self._collGeoms[1]._size)

            self._collGeoms[2]._type = Row.COLLISION_TYPE_ROW
            self._collGeoms[2]._minPt = [ self._drawRects[1][0], self._drawRects[1][1] ]
            self._collGeoms[2]._maxPt = [ self._drawRects[1][0] + self._drawRects[1][2], self._drawRects[1][1] + self._drawRects[1][3] ]
            self._collGeoms[2].setPosition(self._getGridCoordFromScreenCoord(self._collGeoms[2]._minPt[0], cell_size), self._position[1])
            self._collGeoms[2].setSize(self._drawRects[1][2] / cell_size[0], self._size[1])
            #print "Row: type:{} minPt:{} maxPt:{} pos:{} size:{}".format(self._collGeoms[2]._type, self._collGeoms[2]._minPt, self._collGeoms[2]._maxPt, self._collGeoms[2]._position, self._collGeoms[2]._size)

        #print


    def _updateRenderGeometry(self, cell_size):
        """Update the render geometry

           NOTE: Pygame doesn't seem to have a way to modify rectangles in-place (i.e. the Rect type is built on tuples, which are immutable..
           Even move() does not work in-place
           Every time you want to "update" one, you basically make a new one with the updated values)
        """
        if self._gap == 0:
            self._drawRects[0] = self._drawRects[0].move(0, -cell_size[1])

        elif self._gap == self._numBlocks - 1:
            self._drawRects[0] = self._drawRects[0].move(0, -cell_size[1])
        else:
            self._drawRects[0] = self._drawRects[0].move(0, -cell_size[1])
            self._drawRects[1] = self._drawRects[1].move(0, -cell_size[1])


    def _updateCollisionGeometry(self, cell_size):
        # NOTE: In this game, the AABB geometry so happens to be is the same shape as the rendering geometry. That won't be the case in every game

        # NOTE: We make sure to put the gap in slot 0, so we can test for collisions with the ball against the gap 1st, before the row geoms

        # TODO Don't create new CollisionAABB's at every recomputation.. That stresses the garbage collector. Just reinitialize existing geoms. For geom[2], which may or may not be active, set to COLLISION_TYPE_NONE to tell game not to use it for anything

        # Also Note: You could have computed the collision geom based on the render geometry, but multiplying things is more fun
        offset = 0 # Grid offset to put collision 'zone' for score keeping
        self._collGeoms[0]._minPt[0] = (self._gap * self._size[0] * cell_size[0]) + cell_size[0]
        self._collGeoms[0]._minPt[1] = self._position[1] * cell_size[1]

        self._collGeoms[0]._maxPt[0] = (self._gap * self._size[0] * cell_size[0]) + (self._size[0] - 1) * cell_size[0]
        self._collGeoms[0]._maxPt[1] = (self._position[1] + self._size[1] + offset) * cell_size[1]

        self._collGeoms[0].setPosition(self._getGridCoordFromScreenCoord(self._collGeoms[0]._minPt[0], cell_size), self._position[1] + self._size[1] + offset)
        self._collGeoms[0].setSize((self._collGeoms[0]._maxPt[0] - self._collGeoms[0]._minPt[0]) / cell_size[0], 1)

        if self._gap == 0 or self._gap == self._numBlocks - 1:
            # NOTE: Here, we're totally cheating and computing the AABB based on the render geometry.
            # Note rect[0] = left; rect[1] = top; rect[2] = width; rect[3] = height
            self._collGeoms[1]._minPt[0] = self._drawRects[0][0]
            self._collGeoms[1]._minPt[1] = self._drawRects[0][1]

            self._collGeoms[1]._maxPt[0] = self._drawRects[0][0] + self._drawRects[0][2]
            self._collGeoms[1]._maxPt[1] = self._drawRects[0][1] + self._drawRects[0][3]

            self._collGeoms[1].setPosition(self._getGridCoordFromScreenCoord(self._collGeoms[1]._minPt[0], cell_size), self._position[1])
            self._collGeoms[1].setSize(self._drawRects[0][2] / cell_size[0], self._size[1])

        else:
            # Note: You ALWAYS will have at least 2 collision geom, so the if/else conditions could be different. But whatever.. :-D
            self._collGeoms[1]._minPt[0] = self._drawRects[0][0]
            self._collGeoms[1]._minPt[1] = self._drawRects[0][1]

            self._collGeoms[1]._maxPt[0] = self._drawRects[0][0] + self._drawRects[0][2]
            self._collGeoms[1]._maxPt[1] = self._drawRects[0][1] + self._drawRects[0][3]

            self._collGeoms[1].setPosition(self._getGridCoordFromScreenCoord(self._collGeoms[1]._minPt[0], cell_size), self._position[1])
            self._collGeoms[1].setSize(self._drawRects[0][2] / cell_size[0], self._size[1])

            self._collGeoms[2]._minPt[0] = self._drawRects[1][0]
            self._collGeoms[2]._minPt[1] = self._drawRects[1][1]

            self._collGeoms[2]._maxPt[0] = self._drawRects[1][0] + self._drawRects[1][2]
            self._collGeoms[2]._maxPt[1] = self._drawRects[1][1] + self._drawRects[1][3]

            self._collGeoms[2].setPosition(self._getGridCoordFromScreenCoord(self._collGeoms[2]._minPt[0], cell_size), self._position[1])
            self._collGeoms[2].setSize(self._drawRects[1][2] / cell_size[0], self._size[1])

    def _getGridCoordFromScreenCoord(self, coord, cell_size):
        return coord / cell_size[0] # Cells are square, so it doesn't matter which cell_size coordinate we use
