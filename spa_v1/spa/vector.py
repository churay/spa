__doc__ = '''Module for the Vector Implementation'''

import math

### Module Classes ###

class vector(object):
    ### Constructors ###

    def __init__(self, dim, *args):
        dval = args[0] if args else 0.0
        self._dim = dim
        self._dvals = [type(dval)(args[d] if len(args) > d else dval) for d in range(dim)]

    ### Properties ###

    @property
    def dim(self):
        return self._dim

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
        return sum(s * o for s, o in zip(self._dvals, other._dvals))

    def __iadd__(self, other):
        assert self.dim == other.dim, 'Cannot add vectors of differing lengths.'
        for d in range(self.dim): self._dvals[d] += other._dvals[d]
        return self

    def __isub__(self, other):
        assert self.dim == other.dim, 'Cannot subtract vectors of differing lengths.'
        for d in range(self.dim): self._dvals[d] -= other._dvals[d]
        return self

    def __mul__(self, scalar):
        assert isinstance(scalar, (int, float)), 'Cannot multiply vector by non-scalar.'
        return vector(self.dim, *tuple(s * scalar for s in self._dvals))

    def __div__(self, scalar):
        assert isinstance(scalar, (int, float)), 'Cannot divide vector by non-scalar.'
        return vector(self.dim, *tuple(s / scalar for s in self._dvals))

    def __imul__(self, scalar):
        assert isinstance(scalar, (int, float)), 'Cannot multiply vector by non-scalar.'
        for d in range(self.dim): self._dvals[d] = self._dvals[d] * scalar
        return self

    def __idiv__(self, scalar):
        assert isinstance(scalar, (int, float)), 'Cannot divide vector by non-scalar.'
        for d in range(self.dim): self._dvals[d] = self._dvals[d] / scalar
        return self

    def __getitem__(self, index):
        assert index < self.dim, 'Access index must be less than vector length.'
        return self._dvals[index]

    def __setitem__(self, index, scalar):
        assert index < self.dim, 'Access index must be less than vector length.'
        self._dvals[index] = scalar

    def __repr__(self):
        return "vec%d(%s)" % (self.dim, ", ".join(map(str, self._dvals)))

    ### Methods ###

    def length(self):
        return math.sqrt( self % self )

    def normal(self):
        copy = vector(self.dim, *self.dvals)
        copy /= self.length()
        return copy

    def inormal(self):
        self /= self.length()
        return self

    def irotate(self, degrees):
        assert self.dim == 2, 'Cannot rotate a non-2D vector yet.'
        radians = math.radians(degrees)
        self._dvals[0] = (
                math.cos(radians) * self._dvals[0] -
                math.sin(radians) * self._dvals[1])
        self._dvals[1] = (
                math.sin(radians) * self._dvals[0] +
                math.cos(radians) * self._dvals[1])
        return self

    def coerce(self, dtype):
        copy = vector(self.dim, *self.dvals)
        return copy.icoerce(dtype)

    def icoerce(self, dtype):
        for d in range(self.dim): self._dvals[d] = dtype(self._dvals[d])
        return self
