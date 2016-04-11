from row import Row
import pygame
from gameobj import GameObj

class RowManager(GameObj):
    def __init__(self, numRows = 3, updateDelay = 1):
        ''' Initialize the row manager
        '''
        super(RowManager, self).__init__()
        self._numRows = numRows
        self._updateDelay = updateDelay # Note: the row manager keeps the update delay for all its rows
        self._rows = []

        #self._create
        
    # the following function prototypes are placeholders. Update them as needed
    def createRowAndAddToRowList(self, numBlocks=16, yPosition=32, gap=-1):
        # TODO could add checking to make sure we don't add too many items
        self._rows.append( Row(numBlocks, yPosition, gap) )
        pass

    def reInitRow(self):
        pass

    
    def update(self, dt_s, cell_size):
        for row in self._rows:
            row.update(dt_s, cell_size)


    def draw(self, screen, cell_size):
        ''' Draw all rows managed by the row manager
        '''
        for i in xrange(0, len(self._rows)):
            self._rows[i].draw(screen, cell_size)
