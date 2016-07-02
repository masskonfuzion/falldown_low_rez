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

class DotAccessDict(dict):
    def __init__(self, dictObj):
        super(DotAccessDict, self).__init__(dictObj)

    def __getitem__(self, keyString):
        #print "DotAccessDict: running __getitem__({})".format(keyString)
        keys = []
        if '.' in keyString:
            keys = keyString.split('.')
        else:
            keys = [ keyString ]

        #print "DotAccessDict: key={}".format(keys)

        sourceData = self
        for key in keys:
            #print "Searching for key, \"{}\", in obj: {}".format(key, sourceData)
            sourceData = sourceData.get(key)
            if sourceData == None:  # Compare explicitly against None; Don't simply test "if sourceData", because sourceData may be an empty string, which evaluates to False. But an empty string is a valid result to return
                raise KeyError("No key, \"{}\", found in object: {}".format(key, sourceData))
            #print "Found {}".format(sourceData)
        #print "DotAccessDict: got item: {}".format(sourceData)
        return sourceData

    def __setitem__(self, keyString, data):
        #print "DotAccessDict: Calling __setitem__({}) <- {}".format(keyString, data)
        # Find the dict that contains the node to be edited, and set its value
        # i.e. we want to go to the 2nd-to-last level, so if the key is a.b.c, we need to get a.b and modify its [c] item
        if '.' in keyString:
            keyListToLastMutableObj = keyString.split('.')
            indexToUpdate = keyListToLastMutableObj.pop()
            keyStrToLastMutableObj = '.'.join(keyListToLastMutableObj)

            #print "\tDotAccessDict: NOTE - here, DotAccessDict calls __getitem__() to get the object to update"
            mutableObjToChange = self.__getitem__(keyStrToLastMutableObj)

            #mutableObjToChange[indexToUpdate] = data    # I believe this also calls self.__getitem__()
            newVal = {indexToUpdate: data}
            #print "\tDotAccessDict: updating key:{} to {}. Obj = {}".format(keyString, data, newVal)
            mutableObjToChange.update(newVal)
            # The code above works.. but why??
            # Because I've overloaded __getitem__, which allows me to retrieve the object at key.subkey.blah..
            # Because the item retrieved by __getitem__ (or by []) is mutable, I can modify it here
            # (this is kinda cheating.. I _should_ write setitem to locate the mutable obj the same way that getitem does it)
        else:
            self.update({keyString: data})
