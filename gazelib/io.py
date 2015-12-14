'''
Input-Output functions that help to read and write gazefiles in various formats.

'''
import json
import csv

def load_json(filename):
    # load json-type file

    with open(filename, 'r') as data_file:
        data = json.load(data_file)
    return data


def write_json(filename, data):
    # Dump all the JSON in a file.
    with open(filename, 'w') as jsonfile:
        json.dump(data, jsonfile)


def write_fancy_json(filename, data):
    # Write json so that it is readable by humans (rowchange, indent..).
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, sort_keys = True, indent = 4, ensure_ascii=False)


def load_csv_as_dictlist(filename, delimit='\t'):
    # Load a file in csv (common in .gazedata) and return data in JSON suitable
    # for analysis.

    print("Loading csv-file " + filename)

    try:
        ifile = open(filename, "r")
    except Exception as ex:
        print("File loading error: " + str(ex))
        return

    reader = csv.reader(ifile, delimiter = delimit)#"\t")

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

    print("File loaded succesfully. " + str(len(rows)) + " rows read.")
    return rows


def write_dictlist_as_csv(dictlist, target_filename):
    keys = dictlist[0].keys()
    with open(target_filename, 'w') as csvfile:
        fieldnames = keys
        writer = csv.DictWriter(csvfile,
                                fieldnames=fieldnames,
                                dialect='excel')
        writer.writeheader()
        for d in dictlist:
            writer.writerow(d)
