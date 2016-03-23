import os
import tempfile
import gazelib
from sys import float_info
import difflib


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


def get_fixture_filepath(sample_name):
    '''
    Create absolute filepath from sample filename.
    '''
    this_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    full_path = os.path.join(this_dir, 'fixtures', sample_name)
    return full_path


def load_sample(sample_name):
    '''
    Reads from fixtures/ directory
    Access e.g. by: load_sample('sample.common.json')
    '''
    full_path = get_fixture_filepath(sample_name)
    return gazelib.io.load_json(full_path)


def assert_files_equal(self, filepath1, filepath2,
                       msg='Files should be equal but are not'):
    '''
    Assert the content of two files are equal. Do not care about empty spaces
    at the end of the files.
    '''
    with open(filepath1, 'r') as f1, open(filepath2, 'r') as f2:
        # Two lists of lines. Each element is a string that ends with '\n'
        s1 = list(f1.readlines())
        s2 = list(f2.readlines())
    # Trim new lines because it causes problems because
    # hand-written JSON includes trailing empty line where
    # the generated JSON does not.
    s1 = list(map(lambda l: l.rstrip('\n'), s1))
    s2 = list(map(lambda l: l.rstrip('\n'), s2))
    # File names for nice message.
    b1 = filepath1
    b2 = filepath2
    diffs = list(difflib.unified_diff(s1, s2, b1, b2, lineterm='', n=0))
    if len(diffs) != 0:
        # Files not equal
        diffmsg = '\n'.join(diffs)
        msg = msg + ':\n' + diffmsg
        self.fail(msg)
