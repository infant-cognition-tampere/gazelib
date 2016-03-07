import os
import tempfile

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
