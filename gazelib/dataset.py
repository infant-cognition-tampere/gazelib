import logging
import numpy as np
from os.path import join

try:
    from functools32 import lru_cache
except ImportError:
    from functools import lru_cache

class DatasetError(Exception):
    pass

class Dataset(object):
    """ Convenience class for accessing the whole dataset """
    def __init__(self):
        pass

    def get_gazedata(self, name):
        raise DatasetError('Not Implemented')

    def list_gazedatas(self):
        raise DatasetError('Not Implemented')

class CSVDataset(Dataset):
    def __init__(self, directory, filename):
        self.directory = directory
        self.tbt = TBTFile(join(directory, filename))

    @lru_cache(maxsize=32)
    def get_gazedata(self, name):
        return GazedataFile(join(self.directory, name))

    def list_gazedatas(self):
        return np.unique(self.tbt.data['filename'])

class TrialIterator(object):
    """ Iterate trials from dataset """
    def __init__(self, dataset, tbtfilter=None, gazedatafilter=None):

        self.dataset = dataset
        self.gazedatafilter = gazedatafilter

        self.tbtmask = np.array([True] * self.dataset.tbt.data.shape[0])

        if tbtfilter is not None:
            for f in tbtfilter:
                self.tbtmask = self.tbtmask & f(self.dataset.tbt.data)

        self.maskedtbt = self.dataset.tbt.data[self.tbtmask]
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current < self.maskedtbt.shape[0]:
            current_tbt_line = self.maskedtbt[self.current]
            gazedata = self.dataset.get_gazedata(current_tbt_line['filename']).data

            trialid = current_tbt_line['trialid']
            print('fname: %s, trialid: %s' % (current_tbt_line['filename'], str(trialid)))
            retval = gazedata[np.array(map(str, gazedata['trialid'])) == str(trialid)]

            gzdmask = np.array([True] * retval.shape[0])

            if self.gazedatafilter is not None:
                for f in self.gazedatafilter:
                    gzdmask = gzdmask & f(retval)
                    print(gzdmask)

            self.current += 1
            return retval[gzdmask]
        else:
            raise StopIteration

    def next(self):
        return self.__next__()

def seek_past_first_sep(filelike):
    import re

    line = filelike.readline().strip()
    if line != 'sep=' and line != 'sep=,':
        match = re.search('sep=,', str(line))
        if match == None:
            filelike.seek(0)
            return

        print("Seeking to: %i" % match.end())
        filelike.seek(match.end())


def sniff_csv_dialect(filelike):
    from csv import Sniffer

    loc = filelike.tell()

    dialect = Sniffer().sniff(str(filelike.read(4096)), delimiters=[',', ';', '\t'])

    filelike.seek(loc)

    return dialect

def read_csv_names(filelike, dialect, delimiter=None):
    from csv import reader

    delimiter = delimiter if dialect == None else dialect.delimiter
    r = reader(filelike, dialect, delimiter=delimiter)

    return next(r)

    def filter_unwanted(l):
        return filter(lambda x: x!= 'sep=' and x != '', l)

    firstline = filter_unwanted(r.next())
    print('firstline_check: %s' % firstline)
    if len(firstline) == 0:
        print("AEE")
        firstline = filter_unwanted(r.next())

    return firstline

def get_common_name(name):
    substitutes = {'condition': 'stimulus',
        'aoi border violation before disengagement or1000ms (during nvs)':
            'aoi border violation',
        'trial number': 'trialid'}

    try:
        return substitutes[name]
    except KeyError:
        return name

class TBTFile():
    def __init__(self, filename):
        print('Opening %s:' % filename)
        with open(filename, 'r') as f:
            seek_past_first_sep(f)
            dialect = sniff_csv_dialect(f)

            names = [get_common_name(s.lower().strip())
                     for s in read_csv_names(f, dialect)]

            print(names)
            self.names = names
            self.data = np.genfromtxt(f,
                                      skip_header=0,
                                      delimiter=dialect.delimiter,
                                      names=names,
                                      dtype=None)

def _get_common_gzname(name):
    substitutes = {'diameterpupillefteye': 'pupil_l',
                   'diameterpupilrighteye': 'pupil_r',
                   'lefteyepupildiameter': 'pupil_l',
                   'righteyepupildiameter': 'pupil_r',
                   'trialnumber': 'trialid',
                   'onscreen': 'userdefined_1'}

    try:
        return substitutes[name]
    except KeyError:
        return name

def _convert_type(s):
    converters = [int, float, str]

    for c in converters:
        try:
            return c(s)
        except ValueError:
            pass
        except TypeError:
            pass

    return s

class GazedataFile():
    def __init__(self, filename):
        from csv import DictReader

        print("Load GZDF: %s" % filename)
        with open(filename, 'rb') as f:
            self.filename = filename

            seek_past_first_sep(f)
            r = DictReader(f, delimiter='\t')
            data = [{k: _convert_type(v) for k, v in d.items()} for d in r]
            data = {k: [v[k] for v in data] for k in data[0].keys()}

            names = [_get_common_gzname(s.lower().strip()) for s in data.keys()]

            self.data = np.rec.fromarrays(data.values(), names=','.join(names))

        self.data['userdefined_1'][self.data['userdefined_1'] == 'Stimulus'] = 'Face'
