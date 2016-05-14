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
from gameobj import GameObj

class CollisionAABB(GameObj):
    def __init__(self):
        super(CollisionAABB, self).__init__()

        # Size is given in grid cells - screen pixel calculations will be derived from them
        self._minPt = [0, 0]
        self._maxPt = [0, 0]
        self._type = 0    # The idea is to give the collision geom an identifier that lets the game decide how to handle collisions involving geoms of this type

    def __str__(self):
        return "minPt:{} maxPt:{} type:{}".format(self._minPt, self._maxPt, self._type)


    def isColliding(self, other, cell_size):
        ''' Test for collision with the another AABB, aptly named, "other"
        '''
        # Note: This code is optimized for readability, not performance
        if self._maxPt[0] < other._minPt[0] or self._minPt[0] > other._maxPt[0]:
            return False

        if self._maxPt[1] < other._minPt[1] or self._minPt[1] > other._maxPt[1]:
            return False

        return True


    # NOTE: CollisionAABB doesn't have an update() method because 'updates' will be handled by the objects that own the AABB


    def draw(self, screen, cell_size):
        rect = (self._minPt[0], self._minPt[1], self._maxPt[0] - self._minPt[0], self._maxPt[1] - self._minPt[1])
        pygame.draw.rect(screen, (0, 192, 0), rect, 1)

