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
from display_msg import DisplayMessage
from gameobj import GameObj

class DisplayMessageManager(GameObj):
    def __init__(self):
        super(DisplayMessageManager, self).__init__()
        self._font = pygame.font.Font('../asset/font/ARCADE.TTF', 32)   # TODO make it possible to pass in a font object
        self._messages = [] # Start with an empty list
        self._maxMessages = 64  # Preallocate this many message slots; cycle through them
        self._defaultTTL = 3.0 # message time to live, in seconds
        self._nextFreeSlot = 0

        self._preAllocateMemory()

    def _preAllocateMemory(self):
        for i in xrange(0, self._maxMessages):
            self._messages.append(DisplayMessage())

    #def setMessage(self, txtStr="", position=[0,0], txtColor=(128,128,0), ttl=self._defaultTTL):
    def setMessage(self, txtStr="", position=[0,0], txtColor=(128,128,0), ttl=None):
        msg = self._getNextFreeSlot()

        # Ugly workaround ot allowing class member to be default parameter of class member function
        if ttl == None:
            ttl = self._defaultTTL

        if msg:
            msg.create(txtStr, position, txtColor, ttl)
        else:
            raise Exception("Ruh roh! I was unable to find a slot to store the message:{}!".format(txtStr))

    def clear(self):
        del self._messages[:]
        self._preAllocateMemory()
        self._nextFreeSlot = 0

    def getMessage(self, k):
        return self._messages[k]

    def getMessages(self):
        ''' Return message list.
            NOTE Python returns a reference to the list. There's no const protection like in C++, so be careful!
        '''
        return self._messages

    def _getNextFreeSlot(self):
        ''' Totally naive finder -- O(n) - worst-case, iterates through whole list
        '''
        retObj = None

        for msg in self._messages:
            if not msg._alive:
                retObj = msg

        # It's possible to return None here. Make sure to test for that case
        return retObj

    def update(self, dt_s, cell_size, game_stats_obj):
        for msg in self._messages:
            msg.update(dt_s, cell_size)


    def draw(self, screen, cell_size):
        for msg in self._messages:
            if msg._alive:
                textSurface = msg.getTextSurface(self._font)
                xPos = msg._position[0] * cell_size[0]
                if xPos + textSurface.get_size()[0] > screen.get_size()[0]:
                    xPos = screen.get_size()[1] - textSurface.get_size()[0]
                screen.blit(textSurface, (xPos, msg._position[1] * cell_size[1]))
        
