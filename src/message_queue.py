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
        #print "DEBUG Enqueueing message: {}".format(msg_obj)
        self._queue[self._tail] = msg_obj
        self._tail = (self._tail + 1) % len(self._queue)
        if self._empty:
            self._empty = False
        assert (self._tail != self._head)

    def Dequeue(self):
        return_obj = self._queue[self._head]

        peekIndex = (self._head + 1)

        if self._empty:
            return None
        else:
            if self._head == self._tail and not self._empty:
                self._empty = True
            else:
                self._head = peekIndex % len(self._queue)
            return return_obj

    def RegisterListener(self, listener_name, listener, topic):
        """Register a message listener with the MessageQueue
           
           NOTE: This function does not test for containment before adding/replacing items.
        """
        #print "DEBUG Registering Listener: {} {} topic={}".format(listener_name, listener, topic)
        self._registeredListeners[topic].append( { 'name': listener_name, 'ref': listener} )

    def RegisteredListeners(self, topic):
        return self._registeredListeners[topic]
        

    #def Clear(self):
    #    pass

    def Initialize(self, num_slots):
        """Allocate space for the message queue

           NOTE: This function should only ever be run once. The class is not designed for re-allocating memory at runtime
        """
        assert(len(self._queue) == 0)

        for i in range(0, num_slots):
            self._queue.append(None)
            pass
