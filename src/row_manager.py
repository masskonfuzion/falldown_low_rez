from row import Row
import pygame
from gameobj import GameObj

class RowManager(GameObj):
    def __init__(self, numRows = 3, updateDelay = 1):
        ''' Initialize the row manager
        '''
        super(RowManager, self).__init__()
        self._numRows = numRows
        self._updateDelay = updateDelay # Note: the row manager keeps the update delay for all its rows. TODO: Make sure this gets userd, or otherwise delete it
        self._rows = []

        
    # the following function prototypes are placeholders. Update them as needed
    def createRowAndAddToRowList(self, numBlocks=16, yPosition=32, gap=-1, updateDelay=1, cellSize = [10,10]):
        # TODO could add checking to make sure we don't add too many items
        self._rows.append( Row(numBlocks, yPosition, gap, updateDelay) )
        self._rows[ len(self._rows) - 1 ]._computeRenderGeometry(cellSize)
        self._rows[ len(self._rows) - 1 ]._computeCollisionGeometry(cellSize)


    def reInitRow(self):
        # TODO call reinit on rows; probably need to update the function signature here, to take in a row, gap, and position (et. al.?)
        pass

    
    def initLevel(self, num_rows, update_delay, reInitCell, cell_size):
        # TODO Make the following updates:
        # - change num_rows to row_spacing. or something.
        # - Generate rows so that row spacing is consistent all the way down the screen. Mimic scenario where, if spacing is 10, then 7 rows are created (i.e., there's a row created off-screen, at cell 70, to keep spacing consistent on reInit. The goal is to make sure that the spacing of all rows on the screen is ALWAYS the same; so make enough rows to ensure that
        # - And lastly, compute the reInitCell - the cell position where each row should be reInitialized at when a row goes above the top edge of the screen (and make sure it gets returned to the main function.. Perhaps store these properties in a dict or some other object that Python will pass to the function as a reference)
        # - Make sure this initLevel function is smart enough to add new rows to the row list when necessary, and to otherwise reInit rows when it's not necessary to add new rows to the list. Maybe make the function dumb, and have the prorammer specify it in the function call? Or otherwise, have the function compute the number of rows necessary to keep the row spacing even, and add new rows as necessary.
        # TODO actually.. initLevel should belong to the row manager.. That's the entire point
    
        #for i in xrange(0, num_rows):
        if True: # Putting in a BS conditional just to keep indent levels the same. Next project should be to move the initLevel function into the row manager
            self.createRowAndAddToRowList(yPosition=10, updateDelay=update_delay, cellSize = cell_size)
            self.createRowAndAddToRowList(yPosition=20, updateDelay=update_delay, cellSize = cell_size)
            self.createRowAndAddToRowList(yPosition=30, updateDelay=update_delay, cellSize = cell_size)
            self.createRowAndAddToRowList(yPosition=40, updateDelay=update_delay, cellSize = cell_size)
            self.createRowAndAddToRowList(yPosition=50, updateDelay=update_delay, cellSize = cell_size)
            self.createRowAndAddToRowList(yPosition=60, updateDelay=update_delay, cellSize = cell_size)
            self.createRowAndAddToRowList(yPosition=70, updateDelay=update_delay, cellSize = cell_size)


    def update(self, dt_s, cell_size):
        for row in self._rows:
            row.update(dt_s, cell_size)

            # Test rows going off the screen
            if row._position[1] + row._size[1] / 2 == 0:
                #row.reInit(64 - row._size[1] / 2, -1)  # TODO Consider not hardcoding gap to -1; Allow "levels" with pre-determined gap sequences
                row.reInit(70 - row._size[1] / 2, -1)  # TODO decide what to do with new rows.. starting at 70 works if we're starting new rows every 10 grid cells. Figure out how to compute. May need to pass a game logic object into the update() functions (which means creating a game logic class/object)
                # NOTE render geom and collision geom are not recomputed until the next update(). But it's ok; at this point in time, the row is off the screen


    def draw(self, screen, cell_size):
        ''' Draw all rows managed by the row manager
        '''
        for i in xrange(0, len(self._rows)):
            self._rows[i].draw(screen, cell_size)
