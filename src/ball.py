from gameobj import GameObj
import pygame
from collision_aabb import CollisionAABB
from ball_game_state import BallGameState

# TODO Consider putting BallControlState into its own class?
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

        self._objState = BallGameState.UNINITIALIZED
        self._lastRowTouched = -1
        self._lastRowScored = -1
        
        self._update_delay_dict = [ {'init': 0.06, 'inc': 0.0, 'max': 0.06, 'dec': 0.00, 'floor': 0.06 }
                                  , {'init': 0.03, 'inc': 0.0, 'max': 0.03, 'dec': 0.01, 'floor': 0.01 }
                                  ]

        self.resetUpdateDelay()

        # Ball Control State
        self.controlState = BallControlState()

        self._collGeoms = [ CollisionAABB() ]  # A list with 1 elements; we use a list here because it's what our algorithms want


    def changeGameState(self, newState):
        self._objState = newState


    def draw(self, screen, cell_size):
        color = 0,0,255
        
        # TODO: Perhaps give each object a "cell" texture? an image maybe (or SDL primitives?) that constitute 1 cell? And then, based on this object's _size, fill in each cell using the image/SDL primitives
        # SDL rect format is (left, top, width, height)
        my_rect = (self._position[0] * cell_size[0], self._position[1] * cell_size[1], self._size[0] * cell_size[0], self._size[1] * cell_size[1])
        
        pygame.draw.rect(screen, color, my_rect)

        ## DEBUG Draw the collision geometry
        #for geom in self._collGeoms:
        #    geom.draw(screen, cell_size)


    def getGameState(self):
        return self._objState

    def resetUpdateDelay(self):
        # NOTE self._updateDelay_s is a member of gameObj.. But we're not using it here. Thoughts?
        self._update_delay = [ self._update_delay_dict[0]['init'], self._update_delay_dict[1]['init'] ]
        pass


    def update(self, dt_s, cell_size):
        # NOTE: Here's where things get cool. _Every obj has a max speed of exactly 1 grid slot up/down and left/right per frame_. "Speed" is emulated based on update delay, rather than # of spaces moved per update
		# Prepare velocity and stuff based on user input (NOTE: With better design, this call would take place in a function that reads messages off a message queue)
        if self.controlState.leftKeyPressed:
            self._speed[0] = -self._maxSpeed[0]
        elif self.controlState.rightKeyPressed:
            self._speed[0] = self._maxSpeed[0]
        else:
            self._speed[0] = 0


        # Move the ball (if applicable -- only move if update delay has elapsed)
        for i in xrange(0, len(self._accumulator_s)):
            self._accumulator_s[i] += dt_s # NOTE _accumulator_s is part of the gameObj class.. Perhaps break it out to the ball? Because the ball needs a [x,y] accumulator; the rows only need a single value

            if self._accumulator_s[i] > self._update_delay[i]:
                # Reduce the accumulator in this direction
                self._accumulator_s[i] -= self._update_delay[i]

                # Update position in this direction
                self._position[i] += self._speed[i]

                # Recompute the update delay in this direction, using _update_delay_dict
                self._update_delay[i] -= self._update_delay_dict[i]['dec']
                if self._update_delay[i] < self._update_delay_dict[i]['floor']:
                    self._update_delay[i] = self._update_delay_dict[i]['floor']

        self._computeCollisionGeometry(cell_size)

    
    def _computeCollisionGeometry(self, cell_size):
        my_rect = (self._position[0] * cell_size[0], self._position[1] * cell_size[1], self._size[0] * cell_size[0], self._size[1] * cell_size[1])

        self._collGeoms[0]._minPt = [ self._position[0] * cell_size[0], self._position[1] * cell_size[1]]
        self._collGeoms[0]._maxPt = [ self._collGeoms[0]._minPt[0] + self._size[0] * cell_size[0], self._collGeoms[0]._minPt[1] + self._size[1] * cell_size[1] ]


