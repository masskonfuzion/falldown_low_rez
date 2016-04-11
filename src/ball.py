from gameobj import GameObj
import pygame
from collision_aabb import CollisionAABB

class BallControlState:
    def __init__(self):
        self.leftKeyPressed = False
        self.rightKeyPressed = False

    def setLeftKeyPressedTrue(self):
        self.leftKeyPressed = True

    def setLeftKeyPressedFalse(self):
        self.leftKeyPressed = False

    def setRightKeyPressedTrue(self):
        self.rightKeyPressed = True

    def setRightKeyPressedFalse(self):
        self.rightKeyPressed = False

    def reset(self):
        self.leftKeyPressed = False
        self.rightKeyPressed = False

class Ball(GameObj):
    def __init__(self):
        super(Ball, self).__init__()

        self.setSize(2,2)

        # GameObj class supports state-based update intervals. I.e., if the ball is falling, its update interval is maybe shorter (so it moves 1 block every x milliseconds), vs if it is not falling. 
        # ACTUALLY... it's the update delay that changes, depending on state.. So, if falling, update delay x might be slower than update delay y
        # TODO: the update delay dict should define, for each direction: initial amount, increment/decrement amount (0 for instant/constant velocity), max/floor amount
        # TODO - Make it possible to have both increasing AND decreasing update intervals? (e.g. to be able to simulate acceleration AND deceleration?)
        #self.update_delay_dict = { 'on_row' : 0.25
        #                         , 'falling': 0.1
        #                         }

        self._objState = 'falling'
        # TODO: set speed based on state. e.g. When falling, vertical speed is ALWAYS 1 grid slot down the screen per update

        self._update_delay_dict = { 'on_row' : 
                                    { 0 : {'init': 0.01, 'inc': 0, 'max': 0.01, 'dec': 0, 'floor': 0.01}
                                    , 1 : {'init': 0, 'inc': 0, 'max': 0, 'dec': 0, 'floor': 0 }
                                    }
                                  , 'falling' :
                                    { 0 : {'init': 0.1, 'inc': 0, 'max': 0.1, 'dec': 0, 'floor': 0.1 }
                                    , 1 : {'init': 0.1, 'inc': 0.0, 'max': 0.1, 'dec': 0.005, 'floor': 0.050 }
                                    }
                                  }


        self._update_delay = [ self._update_delay_dict[self._objState][0]['init'], self._update_delay_dict[self._objState][1]['init'] ]

        # Ball Control State
        self.controlState = BallControlState()

        self._collGeoms = [ CollisionAABB() ]  # A list with 1 elements; we use a list here because it's what our algorithms want

    def draw(self, screen, cell_size):
        color = 0,0,255
        
        # TODO: Perhaps give each object a "cell" texture? an image maybe (or SDL primitives?) that constitute 1 cell? And then, based on this object's _size, fill in each cell using the image/SDL primitives
        # SDL rect format is (left, top, width, height)
        my_rect = (self._position[0] * cell_size[0], self._position[1] * cell_size[1], self._size[0] * cell_size[0], self._size[1] * cell_size[1])
        
        pygame.draw.rect(screen, color, my_rect)

        # DEBUG Draw the collision geometry
        for geom in self._collGeoms:
            geom.draw(screen, cell_size)


    ##def respondToControllerInput(self):
    ##    """ Set velocity according to user's input

    ##    NOTE:  This function ONLY moves the ball's x/y position.  It does not handle falling due to gravity or
    ##    collisions.
    ##    """

    ##    # NOTE TO SELF:  This is not efficient -- to optimize:  only set the x component
    ##    # if self.direction == -1:
    ##    #     Vector2D_setxy(self.velocity, -self.maxSpeed, self.velocity[1])
    ##    # elif self.direction == 1:
    ##    #     Vector2D_setxy(self.velocity, self.maxSpeed, self.velocity[1])
    ##    # elif self.direction == 0:
    ##    #     Vector2D_setxy(self.velocity, 0, self.velocity[1])

    ##    if self.direction == -1:
    ##        Vector2D_setxy(self.currPhysState.velocity, -self.maxSpeed, self.currPhysState.velocity[1])
    ##    elif self.direction == 1:
    ##        Vector2D_setxy(self.currPhysState.velocity, self.maxSpeed, self.currPhysState.velocity[1])
    ##    elif self.direction == 0:
    ##        Vector2D_setxy(self.currPhysState.velocity, 0, self.currPhysState.velocity[1])


    def update(self, dt_s, cell_size):
        #self.accumulator_s += dt_s

        #if self.accumulator_s > self.update_delay_dict[ self._objState ]:
        #    self.accumulator_s -= self.update_delay_dict[ self._objState ]

        #    # Update position
        #    # NOTE: Here's where things get cool. _Every obj has a max speed of exactly 1 grid slot up/down and left/right per frame_. "Speed" is emulated based on update delay, rather than # of spaces moved per update
        #    self._position[1] += 1

		# Prepare velocity and stuff based on user input (NOTE: With better design, this call would take place in a function that reads messages off a message queue)
        if self.controlState.leftKeyPressed:
            self._speed[0] = -self._maxSpeed[0]
        elif self.controlState.rightKeyPressed:
            self._speed[0] = self._maxSpeed[0]


        # Move the ball (if necessary)

        for i in xrange(0, len(self._accumulator_s)):
            self._accumulator_s[i] += dt_s

            if self._accumulator_s[i] > self._update_delay[i]:
                # Reduce the accumulator in this direction
                self._accumulator_s[i] -= self._update_delay[i]

                # Update position in this direction
                self._position[i] += self._speed[i]

                # TODO - collision detection here?

                # Recompute the update delay in this direction, using _update_delay_dict
                # TODO Add test: if we're decreasing the update delay, then test against floor; if increasing, then test against max
                self._update_delay[i] -= self._update_delay_dict[ self._objState ][i]['dec']
                if self._update_delay[i] < self._update_delay_dict[ self._objState ][i]['floor']:
                    self._update_delay[i] = self._update_delay_dict[ self._objState ][i]['floor']

        self._computeCollisionGeometry(cell_size)

    def _computeCollisionGeometry(self, cell_size):

        my_rect = (self._position[0] * cell_size[0], self._position[1] * cell_size[1], self._size[0] * cell_size[0], self._size[1] * cell_size[1])

        self._collGeoms[0]._minPt = [ self._position[0] * cell_size[0], self._position[1] * cell_size[1]]
        self._collGeoms[0]._maxPt = [ self._collGeoms[0]._minPt[0] + self._size[0] * cell_size[0], self._collGeoms[0]._minPt[1] + self._size[1] * cell_size[1] ]


