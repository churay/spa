__doc__ = '''Module for the Bezier Function Implementation'''

import math
import vector

### Module Classes ###

class bezier(object):
    ### Constructors ###

    def __init__(self, *args):
        err = 'Improperly defined Bezier curve.'
        assert len(args) % 2 == 0, err
        assert all(0.0 <= cx <= 1.0 for cx in args[::2]), err

        self._cpoints = [0.0, 0.0] + list(args) + [1.0, 1.0]
        self._cpoints = [vector.vector(2, cx, cy) for cx, cy 
            in zip(self._cpoints[::2], self._cpoints[1::2])]
        self._degree = len(self._cpoints) - 1

    ### Properties ###

    @property
    def degree(self):
        return self._degree

    ### Methods ###

    def evaluate(self, t):
        assert 0.0 <= t <= 1.0, 'Invalid evaluation parameter; must be in [0, 1].'

        # TODO(JRC): This was ripped directly from Wikipedia, so some semblance
        # of actual knowledge needs to be embedded into these variables and their
        # evaluation (perhaps using De-Castlejau instead).
        evals = [1.0 * v for v in self._cpoints]
        for k in range(1, len(self._cpoints) + 1):
            for i in range(len(self._cpoints) - k):
                evals[i] = (1.0 - t) * evals[i] + t * evals[i + 1]

        return evals[0][1]
