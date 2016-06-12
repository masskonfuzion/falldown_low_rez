class DotAccessDict(dict):
    def __init__(self, dictObj):
        super(DotAccessDict, self).__init__(dictObj)

    def __getitem__(self, keyString):
        keys = []
        if '.' in keyString:
            keys = keyString.split('.')
        else:
            keys = [ keyString ]

        sourceData = self
        for key in keys:
            #print "Searching for {} in {}".format(key, sourceData)
            sourceData = sourceData.get(key)
        if not sourceData:
            raise KeyError("No key {} found in dict")
        return sourceData

    def __setitem__(self, keyString, data):
        # Find the dict that contains the node to be edited, and set its value
        # i.e. we want to go to the 2nd-to-last level, so if the key is a.b.c, we need to get a.b and modify its [c] item
        if '.' in keyString:
            keyListToLastMutableObj = keyString.split('.')
            indexToUpdate = keyListToLastMutableObj.pop()
            keyStrToLastMutableObj = '.'.join(keyListToLastMutableObj)

            mutableObjToChange = self.__getitem__(keyStrToLastMutableObj)
            mutableObjToChange[indexToUpdate] = data    # I believe this also calls self.__getitem__()
            # The code above works.. but why??
            # Because I've overloaded __getitem__, which allows me to retrieve the object at key.subkey.blah..
            # But because the item retrieved by __getitem__ (or by []) is mutable, I can modify it here
        else:
            self.update({keyString: data})
