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
        json.dump(data, outfile, sort_keys=True,
                  indent=4, ensure_ascii=False)


def load_csv_as_dictlist(filename, delimit='\t', silent=True):
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

    reader = csv.reader(ifile, delimiter=delimit)

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


def write_dictlist_as_csv(target_filename, dictlist, delimit='\t'):
    '''
    Write given list of dicts to a file as CSV. Each dict is required
    to have key for each column name. The column names are read from the
    first dict.
    '''
    keys = dictlist[0].keys()
    with open(target_filename, 'w') as csvfile:
        fieldnames = keys
        writer = csv.DictWriter(csvfile,
                                fieldnames=fieldnames,
                                delimiter=delimit)
        writer.writeheader()
        for d in dictlist:
            writer.writerow(d)
