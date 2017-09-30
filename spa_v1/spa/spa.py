__doc__ = '''Module for SPA ((Sequential Picture Amalgamator)) Globals'''

import os, sys

### Module Functions ###

def display_status(item, curr, total):
    sys.stdout.write('\r')
    sys.stdout.write('  processing %s %d/%d...' % (item, curr+1, total))
    if curr + 1 >= total: sys.stdout.write('\n')
    sys.stdout.flush()
