from json import JSONEncoder
import numpy


# Solver Borislav Hadzhiev at
#       https://bobbyhadz.com/blog/python-typeerror-object-of-type-ndarray-is-not-json-serializable
class NumpyEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)
