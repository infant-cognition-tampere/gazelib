# -*- coding: utf-8 -*-
'''
Input-Output functions that help to read and write gaze data.

'''
import json
import csv


def load_json(filename):
    '''
    Load json-type file and return its contents as python object.

    Raise IOError if loading failed.
    Raise ValueError if JSON decoding failed.

    Note: IOError might vary between environments.
    See: http://stackoverflow.com/q/15032108/638546
    '''
    # It seems that with open... hides exception.
    data_file = open(filename, 'r')  # Can raise IOError
    try:
        data = json.load(data_file)
    finally:
        # Regardless whether JSON load fails, close the file.
        data_file.close()
    return data


def write_json(filename, data, human_readable=False):
    '''
    Dump data to a given JSON file. File is created if it does not exist.

    Raise TypeError if data is not serializable.
    '''
    with open(filename, 'w') as jsonfile:
        if not human_readable:
            json.dump(data, jsonfile)
        else:
            # ensure_ascii=False
            #   'True' would turn non-ascii characters such
            #   as ä and ö to escaped unicode sequences: \uXXXX,
            #   turning text hard to read.
            # separators
            #   Without setting separators explicitly,
            #   Python 2.7 and Python 3.5 would produce different output.
            #   See https://docs.python.org/3/library/json.html#json.dump
            json.dump(data, jsonfile, sort_keys=True, indent=4,
                      ensure_ascii=False, separators=(',', ': '))


def write_fancy_json(filename, data):
    '''
    Write JSON so that it is readable by humans (new lines, indent..).

    Raise (see write_json)
    '''
    return write_json(filename, data, human_readable=True)


def load_csv_as_dictlist(filepath, delimiter='\t'):
    '''
    Load a file in csv (common in .gazedata) and return data as
    list of dicts. Each dict contains the column names as keys and
    cell values as dict values.

    Raise IOError if filepath is invalid
    Raise ValueError if file is not CSV formatted.
    '''

    ifile = open(filepath, 'r')  # Can raise IOError

    try:
        reader = csv.reader(ifile, delimiter=delimiter)

        rownum = 0
        rows = []
        for row in reader:
            items = {}
            if rownum == 0:
                # headers
                headers = row
            else:
                for inum, i in enumerate(headers):
                    items[i] = row[inum]
                rows.append(items)
            rownum += 1
    finally:
        ifile.close()

    if rows == []:
        raise ValueError('CSV file is not correctly formatted.')

    return rows


def write_dictlist_as_csv(target_filename, dictlist, headers=None,
                          delimiter='\t'):
    '''
    Write given list of dicts to a file as CSV. Each dict is required
    to have key for each column name. The column names are read from the
    first dict.

    Parameters:
        target_filename:
            A path to target file
        dictlist:
            A list of dicts. Each dict is required to have same set of keys.
        headers:
            Optional list of keys. Defines the order of columns.
        delimiter:
            Delimiter character.
    '''
    # Normalize to iterable
    dictlist = iter(dictlist)
    first = next(dictlist)
    # Headers
    if headers is None:
        fieldnames = first.keys()
    else:
        fieldnames = headers
    # Write
    with open(target_filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=fieldnames,
                                lineterminator='\n',
                                delimiter=delimiter)
        writer.writeheader()
        writer.writerow(first)
        for d in dictlist:
            writer.writerow(d)
