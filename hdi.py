import math
import operator as op
import itertools as it
import collections as cl

HDI = cl.namedtuple('HDI', 'lower, upper')

def hdi(values, ci=0.95):
    values = sorted(filter(math.isfinite, values))
    if not values:
        raise ValueError('Empty data set')

    n = len(values)
    exclude = n - math.floor(n * ci)

    left = it.islice(values, exclude)
    right = it.islice(values, n - exclude, None)

    diffs = ((x, y, y - x) for (x, y) in zip(left, right))
    (*args, _) = min(diffs, key=op.itemgetter(-1))

    return HDI(*args)
