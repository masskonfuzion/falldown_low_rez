import pygame
import sys

class GameObj(object):
    ''' Game Object Class purpose-built for Low Rez Jam 2016. The game must take place in a 64x64 grid
    '''
    def __init__(self):
        self._position = [0, 0] # Position is given in terms of "top-left". i.e., (0,0) is the top-left corner of the rect at position (0,0)
        self._size = [2, 2]     # default size is 2 "pixels" by 2 pixels (1 "pixel" is a square on the 64x64 grid
        self._speed = [0, 0]    # "speed" is NOT velocity! It is given in terms of the # of pixels the obj can move per update delay
        self._maxSpeed = [0, 0] # Max speeds in the x/y directions
        self._image = None
        self._rect = None

        self.accumulator_s = 0.0 # TODO - delete? replace with _accumulator?
        self.update_delay_s = 1.0 # # of seconds that must pass before next update for this object.
                                  # TODO - delete update_delay_s? We'll use the dict instead?

        self.update_delay_dict = {} # key/value pairs, e.g.: { 'on_row': 0.25, 'falling': 0.1 }
        self._objState = 0 # object's state.
        self._accumulator_s = [0.0, 0.0]

    def setSize(self, sx, sy):
        ''' Set the size of the object, in terms of grid squares
        '''
        self._size[0] = sx
        self._size[1] = sy

    def setPosition(self, gx, gy):
        ''' Set the object's position on the grid (gx, gy)
        '''
        self._position[0] = gx
        self._position[1] = gy

    def setSpeed(self, sx, sy):
        ''' Set "speed" of object
            NOTE: Speed is defined as the # of "pixels" the object will move per update cycle. An update cycle is an interval of time the object must wait before making one move
        '''
        self._speed[0] = sx
        self._speed[1] = sy

    def setMaxSpeed(self, sx, sy):
        ''' Set max speed of object
            NOTE: Speed is defined as the # of "pixels" the object will move per update cycle. An update cycle is an interval of time the object must wait before making one move
        '''
        self._maxSpeed[0] = sx
        self._maxSpeed[1] = sy

    def update(self, dt_s, cell_size, game_stats_obj):
        ''' Update (which really involves simply counting dt and figuring out whether or not we should be moving or sitting still)
        '''
        # NOTE: game_stats_obj is an object that has vital game info, e.g. score, level, etc. For this base class, we should consider using **args or some other construct that allows flexibility for many different inputs to the Update() function
        # cell_size is a 2-item list passed in from the application
        # dt_s is delta-time, in seconds
        raise NotImplementedError

    def draw(self, screen, cell_size):
        # Might not need draw() if we're blitting images to the screen surface
        # cell_size is a 2-item list passed in from the application
        raise NotImplementedError
        pass

    def loadImage(self, filename):
        self._image = pygame.image.load(filename)
        self._rect = self._image.get_rect()



