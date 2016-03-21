import os
import tempfile
from sys import float_info

def get_temp_filepath(file_name):
    '''
    Generate filepath for a file that is needed only briefly.
    '''
    # Absolute path to temp dir.
    p = tempfile.mkdtemp()
    return os.path.join(p, file_name)

def remove_temp_file(abs_filepath):
    '''
    Remove file created by the tempfile.mkdtemp
    Warning! Is capable to remove any file and its directory.
    '''
    d = os.path.dirname(abs_filepath)
    os.remove(abs_filepath)
    os.rmdir(d)

def frange(x, y, jump=1.0):
    '''
    Range for floats.
    Source: http://stackoverflow.com/a/7267280/638546
    '''
    i = 0
    x0 = x
    while x + float_info.epsilon < y:
        yield x
        i += 1
        x = x0 + i * jump
