__doc__ = '''Module for the Disjoint Set Structure Implementation'''

import collections

### Module Classes ###

class dsets(object):
    ### Constructors ###

    def __init__(self, size):
        self._dsets = [-1] * size

    ### Operators ###

    def __repr__(self):
        return str(self.tabulate())

    ### Methods ###

    def union(self, dset1, dset2):
        dset1, dset2 = tuple(self.find(d) for d in (dset1, dset2))
        dsize1, dsize2 = tuple(self._dsets[d] for d in (dset1, dset2))

        if dset1 != dset2:
            if abs(dsize1) >= abs(dsize2):
                self._dsets[dset1] = dsize1 + dsize2
                self._dsets[dset2] = dset1
            else:
                self._dsets[dset1] = dset2
                self._dsets[dset2] = dsize1 + dsize2

    def find(self, dset):
        if self._is_delegate(dset):
            return dset
        else:
            self._dsets[dset] = self.find(self._dsets[dset])
            return self._dsets[dset]

    def length(self):
        return sum((int(self._is_delegate(d)) for d in range(len(self._dsets))), 0)

    def tabulate(self):
        table = collections.defaultdict(list)
        for dset in range(len(self._dsets)):
            table[self.find(dset)].append(dset)
        return table

    ### Helpers ###

    def _is_delegate(self, dset):
        return self._dsets[dset] < 0
