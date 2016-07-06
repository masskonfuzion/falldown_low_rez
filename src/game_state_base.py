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

# NOTE: States know how to get from themselves to another state.
# States get a pointer/reference to the engine, to be able to interact with the stack of states

class GameStateBase(object):
    """Base/Interface class for game states"""
    def __init__(self):
        self._name = "UNITIALIZED"

    #def __str__(self):
    #    return self._name

    def SetName(self, stateName):
        """Set the state's name (used primarily for debugging)"""
        self._name = stateName

    def Init(self, engineRef, takeWith=None):
        raise NotImplementedError("Init() must be implemented by a subclass")

    def Cleanup(self):
        # NOTE this class is a port from a C++ class. Because Python is garbage-collected, Cleanup() is probably not necessary here. But it's included for completeness
        raise NotImplementedError("Cleanup() must be implemented by a subclass")

    # TODO Consider changing "pause" to "PushState" or something; doesn't HAVE to be 'pause'
    def Pause(self):
        raise NotImplementedError("Pause() must be implemented by a subclass")

    # TODO Consider changing "resume" to "PopState" or something; doesn't HAVE to be 'resume'
    def Resume(self):
        raise NotImplementedError("Resume() must be implemented by a subclass")

    def ProcessEvents(self, engineRef):
        raise NotImplementedError("ProcessEvents() must be implemented by a subclass")

    def ProcessCommands(self, engineRef):
        raise NotImplementedError("ProcessCommands() must be implemented by a subclass")

    def Update(self, engineRef, dt_s, cell_size):
        raise NotImplementedError("Update() must be implemented by a subclass")

    def PreRenderScene(self, engineRef):
        raise NotImplementedError("PreRenderScene() must be implemented by a subclass")

    def RenderScene(self, engineRef):
        raise NotImplementedError("RenderScene() must be implemented by a subclass")

    def PostRenderScene(self, engineRef):
        raise NotImplementedError("PostRenderScene() must be implemented by a subclass")

    def ChangeState(self, toState, engineRef):
        engineRef.changeState(toState)
        # NOTE toState should be a state object reference (i.e., it should probably be a state object that is a member of the game engine class already
