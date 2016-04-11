import pygame
from gameobj import GameObj

class CollisionAABB(GameObj):
    def __init__(self):
        super(CollisionAABB, self).__init__()

        # Size is given in grid cells - screen pixel calculations will be derived from them
        self._minPt = [0, 0]
        self._maxPt = [0, 0]

    def isColliding(self, other, cell_size):
        ''' Test for collision with the another AABB, aptly named, "other"
        '''

        # Note: This code is optimized for readability, not performance
        #myMin = [ self._position[0], self._position[1] ]
        #myMax = [ self._position[0] + self._size[0] * cell_size[0], self._position[1] + self._size[1] * cell_size[1] ]

        #otherMin = [ other._position[0], other._position[1] ]
        #otherMax = [ other._position[0] + other._size[0] * cell_size[0], other._position[1] + other._size[1] * cell_size[1] ]

        #if myMax[0] < otherMin[0] or myMin[0] > otherMax[0]:
        #    return False

        #if myMax[1] < otherMin[1] or myMin[1] > otherMax[1]:
        #    return False

        if self._maxPt[0] < other._minPt[0] or self._minPt[0] > other._maxPt[0]:
            return False

        if self._maxPt[1] < other._minPt[1] or self._minPt[1] > other._maxPt[1]:
            return False

        return True

    # NOTE: CollisionAABB doesn't have an update() method because 'updates' will be handled by the objects that own the AABB


    def draw(self, screen, cell_size):
        rect = (self._minPt[0], self._minPt[1], self._maxPt[0] - self._minPt[0], self._maxPt[1] - self._minPt[1])
        pygame.draw.rect(screen, (0, 192, 0), rect, 1)

