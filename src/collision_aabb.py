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
        if self._maxPt[0] < other._minPt[0] or self._minPt[0] > other._maxPt[0]:
            return False

        if self._maxPt[1] < other._minPt[1] or self._minPt[1] > other._maxPt[1]:
            return False

        return True


    # NOTE: CollisionAABB doesn't have an update() method because 'updates' will be handled by the objects that own the AABB


    def draw(self, screen, cell_size):
        rect = (self._minPt[0], self._minPt[1], self._maxPt[0] - self._minPt[0], self._maxPt[1] - self._minPt[1])
        pygame.draw.rect(screen, (0, 192, 0), rect, 1)

