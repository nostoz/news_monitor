import time
import json

def timeit(f):

    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        # print('func:%r args:[%r, %r] took: %2.4f sec' %(f.__name__, args, kw, te-ts))
        print('func:%r took: %2.4f sec' %(f.__name__, te-ts))
        return result

    return timed

def read_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)