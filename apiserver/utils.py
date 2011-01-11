# encoding: utf-8

import time   
from functools import wraps                                             

class timed(object):
    def __init__(self, callback=None):
        self.callback = callback
        
    def __call__(self, fn):
        @wraps(fn)
        def timed_fn(*vargs, **kwargs):
            start = time.time()
            result = fn(*vargs, **kwargs)
            finish = time.time()
            duration = round(finish-start, 2)
            msg = "Executed {module}.{name} in {time} seconds.".format(
                module=fn.__module__, name=fn.__name__, time=duration)
            if self.callback:
                self.callback(msg)
            else:
                print msg
            return result

        return timed_fn
