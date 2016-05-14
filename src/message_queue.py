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

"""
Queue is a ring-based array/queue. It needs:
* Enqueue(Message) (or, call it PutMessage or PutEvent or whatever)
** Place item in list
** Advance tail, i.e. tail = (tail + 1) % length
* Dequeue() (or, call it GetEvent or GetMessages or whatever)
** Return item at head
** head = (head + 1) % length
* Clear()
** Set head = tail
* RegisterListener(listener)
* RegisteredListeners()
** Return a reference to the queue data member
* _queue = list
* _registeredListeners = list
* _head = int
* _tail = int
"""

import collections

class MessageQueue:
    def __init__(self):
        self._queue = []
        self._registeredListeners = collections.defaultdict(list) # A list of dict objects. The dict objects contain the Listener Name (for lookups) and a reference to the listener instance
        self._head = 0
        self._tail = 0
        self._empty = True

    def Enqueue(self, msg_obj):
        """ Enqueue a message object

            Message objects contain a topic and a payload. Still trying to work out exactly how to design message objects. In Python, they can be a dict
        """
        if self._empty:
            self._empty = False
        else:
            self._tail = (self._tail + 1) % len(self._queue)
            assert (self._tail != self._head) # If tail == head, that means we've enqueued too many messages and we're wrapping around
        self._queue[self._tail] = msg_obj
        #print "DEBUG Enqueued message: {}".format(msg_obj)

    def Dequeue(self):
        if self._empty:
            return None

        else:
            return_obj = self._queue[self._head]

            if self._head == self._tail and not self._empty:
                self._empty = True
            else:
                self._head = (self._head + 1) % len(self._queue)

            #print "DEBUG Dequeued message: {}".format(return_obj)
            return return_obj

    def RegisterListener(self, listener_name, listener, topic):
        """Register a message listener with the MessageQueue
           
           NOTE: This function does not test for containment before adding/replacing items.
        """
        #print "DEBUG Registering Listener: {} {} topic={}".format(listener_name, listener, topic)
        self._registeredListeners[topic].append( { 'name': listener_name, 'ref': listener} )

    def RegisteredListeners(self, topic):
        return self._registeredListeners[topic]
        

    def Clear(self):
        self._head = 0
        self._tail = 0
        del self._queue[:]
        self._empty = True

    def Initialize(self, num_slots):
        """Allocate space for the message queue

           NOTE: This function should only ever be run once. The class is not designed for re-allocating memory at runtime
        """
        assert(len(self._queue) == 0)

        for i in range(0, num_slots):
            self._queue.append(None)
            pass
