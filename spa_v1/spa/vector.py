__doc__ = '''Module for the Vector Implementation'''

import math

### Module Classes ###

class vector(object):
    ### Constructors ###

    def __init__(self, dim, *args, dtype=None):
        dval = args[0] if args else 0.0
        self._dim = dim
        self._dtype = dtype or type(dval)
        self._dvals = [self._dtype(args[d] if len(args) > d else dval) for d in range(dim)]

    ### Properties ###

    @property
    def dim(self):
        return self._dim

    @property
    def dtype(self):
        return self._dtype

    @property
    def dvals(self):
        return tuple(self._dvals)

    ### Operators ###

    def __add__(self, other):
        assert self.dim == other.dim, 'Cannot add vectors of differing lengths.'
        return vector(self.dim, *tuple(s + o for s, o in zip(self._dvals, other._dvals)))

    def __sub__(self, other):
        assert self.dim == other.dim, 'Cannot subtract vectors of differing lengths.'
        return vector(self.dim, *tuple(s - o for s, o in zip(self._dvals, other._dvals)))

    def __mod__(self, other):
        assert self.dim == other.dim, 'Cannot dot vectors of differing lengths.'
        return sum(self._dtype(s * o) for s, o in zip(self._dvals, other._dvals))

    def __iadd__(self, other):
        assert self.dim == other.dim, 'Cannot add vectors of differing lengths.'
        for d in range(self.dim): self._dvals[d] += self._dtype(other._dvals[d])
        return self

    def __isub__(self, other):
        assert self.dim == other.dim, 'Cannot subtract vectors of differing lengths.'
        for d in range(self.dim): self._dvals[d] -= self._dtype(other._dvals[d])
        return self

    def __mul__(self, scalar):
        assert isinstance(scalar, (int, float)), 'Cannot multiply vector by non-scalar.'
        return vector(self.dim, *tuple(self._dtype(s * scalar) for s in self._dvals))

    def __div__(self, scalar):
        assert isinstance(scalar, (int, float)), 'Cannot divide vector by non-scalar.'
        return vector(self.dim, *tuple(self._dtype(s / scalar) for s in self._dvals))

    def __imul__(self, scalar):
        assert isinstance(scalar, (int, float)), 'Cannot multiply vector by non-scalar.'
        for d in range(self.dim): self._dvals[d] = self._dtype(self._dvals[d] * scalar)
        return self

    def __idiv__(self, scalar):
        assert isinstance(scalar, (int, float)), 'Cannot divide vector by non-scalar.'
        for d in range(self.dim): self._dvals[d] = self._dtype(self._dvals[d] / scalar)
        return self

    def __getitem__(self, index):
        assert index < self.dim, 'Access index must be less than vector length.'
        return self._dvals[index]

    def __setitem__(self, index, scalar):
        assert index < self.dim, 'Access index must be less than vector length.'
        self._dvals[index] = self._dtype(scalar)

    def __repr__(self):
        return "vec%d(%s)" % (self.dim, ",".join(self._dvals))

    ### Methods ###

    def length(self):
        return math.sqrt( self % self )

    def normalize(self):
        return self /= self.length()
