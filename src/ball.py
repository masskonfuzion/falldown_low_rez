from gameobj import GameObj
import pygame

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
                                    { 0 : {'init': 0.25, 'inc': 0, 'max': 0.25, 'dec': 0, 'floor': 0.25}
                                    , 1 : {'init': 0, 'inc': 0, 'max': 0, 'dec': 0, 'floor': 0 }
                                    }
                                  , 'falling' :
                                    { 0 : {'init': 0.25, 'inc': 0, 'max': 0.25, 'dec': 0, 'floor': 0.25 }
                                    , 1 : {'init': 0.1, 'inc': 0.1, 'max': 0.1, 'dec': 0.005, 'floor': 0.005 }
                                    }
                                  }

        self._update_delay = [ self._update_delay_dict[self._objState][0]['init'], self._update_delay_dict[self._objState][1]['init'] ]


    def draw(self, screen, cell_size):
        color = 0,0,255
        
        # TODO: Perhaps give each object a "cell" texture? an image maybe (or SDL primitives?) that constitute 1 cell? And then, based on this object's _size, fill in each cell using the image/SDL primitives
        # SDL rect format is (left, top, width, height)
        my_rect = (self._position[0] * cell_size[0], self._position[1] * cell_size[1], self._size[0] * cell_size[0], self._size[1] * cell_size[1])
        
        pygame.draw.rect(screen, color, my_rect)

    def update(self, dt_s, cell_size):
        #self.accumulator_s += dt_s

        #if self.accumulator_s > self.update_delay_dict[ self._objState ]:
        #    self.accumulator_s -= self.update_delay_dict[ self._objState ]

        #    # Update position
        #    # NOTE: Here's where things get cool. _Every obj has a max speed of exactly 1 grid slot up/down and left/right per frame_. "Speed" is emulated based on update delay, rather than # of spaces moved per update
        #    self._position[1] += 1

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
                self._update_delay[i] -= self._update_delay_dict[ self._objState ][i]['inc']
                if self._update_delay[i] < self._update_delay_dict[ self._objState ][i]['floor']:
                    self._update_delay[i] = self._update_delay_dict[ self._objState ][i]['floor']
