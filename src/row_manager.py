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
from row import Row
import pygame
from gameobj import GameObj

class RowManager(GameObj):
    def __init__(self, numRows = 3, updateDelay = 1):
        ''' Initialize the row manager
        '''
        super(RowManager, self).__init__()
        self._numRows = numRows
        self._updateDelay = updateDelay # Note: the row manager keeps the update delay for all its rows. TODO: Make sure this gets used, or otherwise delete it
        self._rows = []
        self._rowSpacing = 6
        self._rowReinitPos = 0
        self._min_gap_diff = 0 # gap diff is the dist between the gap on 'this' row and 'the next row'
        self._max_gap_diff = 3
        # TODO come up with a way to evaluate difficulty. e.g., don't make the player cross the entire length of the screen 2x in a row. Figure out how to dole out consecutive same-gap rows (e.g. 2 or 3 consecutive rows each with the same gap).. stuff like that. Make the game follow a predictable sequence of row gap spacings; but let the actual gaps themselves be random. This way, high scores mean something.

    def _getNewGapBasedOnDifficulty(self, prevGap):
        gap = random.randint(0, self._rows[0]._numBlocks - 1) # Get numBlocks from a row because, for some reason, roe manager does not store numBlocks.. Weird.. What was I thinking??
        while abs(gap - prevGap) < self._min_gap_diff or abs(gap - prevGap) > self._max_gap_diff:
            gap = random.randint(0, self._rows[0]._numBlocks - 1)
        return gap

    # the following function prototypes are placeholders. Update them as needed
    def createRowAndAddToRowList(self, numBlocks=16, yPosition=32, gap=-1, updateDelay=1, cellSize = [10,10]):
        # TODO could add checking to make sure we don't add too many items

        # If this is the 1st row, simply create a random gap
        if not self._rows:
            self._rows.append( Row(numBlocks, yPosition, gap, updateDelay) )
        else:
            prevGap = self._rows[ len(self._rows) - 1]._gap
            gap = self._getNewGapBasedOnDifficulty(prevGap)
            self._rows.append( Row(numBlocks, yPosition, gap, updateDelay) )

        self._rows[ len(self._rows) - 1 ]._createRenderGeometry(cellSize)
        self._rows[ len(self._rows) - 1 ]._createCollisionGeometry(cellSize)


    def reInitRow(self):
        # TODO call reinit on rows; probably need to update the function signature here, to take in a row, gap, and position (et. al.?)
        # TODO orrrrr delete reInitRow(), because it's not used? Clean up your code, foo!
        pass

    
    def initLevel(self, row_spacing, update_delay, cell_size):
        if self._rows:
            del self._rows[:] # Apparently there is no clear() for lists

        r = Row() # create throwaway row, just to get default row size (used in calculation of # rows and reinit position
        self._rowSpacing = row_spacing # store the row spacing so we can change it, from the Application class, in later calls to reInitLevel

        # Compute the apparent spacing so the the amount of space between rows is the actual specified # (i.e., the not the specified # - row height)
        apparent_row_spacing = row_spacing + r._size[1]

        # NOTE Probably don't need to store self._numRows, because we can get that value from len(self._rows). Dah well... Too late to fix! Scrambling to submit game!
        self._numRows = (64 / apparent_row_spacing) + 1 # We can hardcode 64 because the rules of the game jam for which we're making this game require a 64x64 grid
        self._rowReinitPos = self._numRows * apparent_row_spacing

        #print "DEBUG RowManager rowSpacing:{} numRows:{} rowReinitPos:{}".format(self._rowSpacing, self._numRows, self._rowReinitPos)
    
        self.changeUpdateDelay(update_delay)

        for i in xrange(0, self._numRows):
            self.createRowAndAddToRowList(yPosition=32 + apparent_row_spacing * (i + 1), updateDelay=update_delay, cellSize = cell_size)

    def changeUpdateDelay(self, newUpdateDelay):
        self._updateDelay = newUpdateDelay

    def updateDifficulty(self, engineRef):
        #print "Row Manager executing updateDifficulty()"
        # TODO Put caps on these min and max gap differences
        if engineRef.vital_stats.level % 3 == 0:
            self._min_gap_diff += 1
            self._max_gap_diff += 1


    def update(self, dt_s, cell_size, game_stats_obj):
        # TODO pass in game difficulty information, so we can adjust the method of assigning gaps
        self._accumulator_s[1] += dt_s

        if self._accumulator_s[1] > self._updateDelay:
            self._accumulator_s[1] -= self._updateDelay

            for i in range(0, len(self._rows)):
                row = self._rows[i]

                row.update(dt_s, cell_size, game_stats_obj)

                # Test rows going off the screen
                if row._position[1] + row._size[1] / 2 == 0:
                    prevGap = self._rows[ (i - 1) % len(self._rows) ]._gap
                    newGap = self._getNewGapBasedOnDifficulty(prevGap)
                    row.reInit(cell_size, self._rowReinitPos - row._size[1] / 2, newGap, game_stats_obj)

                    # NOTE render geom and collision geom are not recomputed until the next update(). But it's ok; at this point in time, the row is off the screen


    def draw(self, screen, cell_size):
        ''' Draw all rows managed by the row manager
        '''
        for i in xrange(0, len(self._rows)):
            self._rows[i].draw(screen, cell_size)
