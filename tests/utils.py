import contextlib
import os


@contextlib.contextmanager
def workingdir(d):
    od = os.getcwd()
    os.chdir(d)
    try:
        yield
    finally:
        os.chdir(od)
