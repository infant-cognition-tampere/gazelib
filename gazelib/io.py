# -*- coding: utf-8 -*-
'''
Input-Output functions that help to read and write gaze data.

'''
import json
import csv


def load_json(filename):
    '''
    Load json-type file and return its contents as python object.
    '''

    with open(filename, 'r') as data_file:
        data = json.load(data_file)
    return data


def write_json(filename, data):
    '''
    Dump data to a given JSON file. File is created if does not exist.
    '''
    with open(filename, 'w') as jsonfile:
        json.dump(data, jsonfile)


def write_fancy_json(filename, data):
    '''
    Write JSON so that it is readable by humans (new lines, indent..).
    '''
    with open(filename, 'w') as outfile:
        # ensure_ascii=False
        #   'True' would turn non-ascii characters such
        #   as ä and ö to escaped unicode sequences: \uXXXX, turning text
        #   hard to read.
        # separators
        #   Without setting separators explicitly,
        #   Python 2.7 and Python 3.5 would produce different output.
        #   See https://docs.python.org/3/library/json.html#json.dump
        json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False,
                  separators=(',', ': '))


def load_csv_as_dictlist(filename, delimiter='\t', silent=True):
    '''
    Load a file in csv (common in .gazedata) and return data as
    list of dicts. Each dict contains the column names as keys and
    cell values as dict values.
    '''

    if not silent:
        print("Loading csv-file " + filename)

    try:
        ifile = open(filename, "r")
    except Exception as ex:
        if not silent:
            print("File loading error: " + str(ex))
        return

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

    ifile.close()

    if not silent:
        print("File loaded succesfully. " + str(len(rows)) + " rows read.")

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
