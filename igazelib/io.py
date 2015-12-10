'''
Input-Output functions that help to read and write gazefiles in various formats.

'''
import json
import csv

# Configuration



def load_JSON(filename):
    # load json-type file

    with open(filename) as data_file:
        data = json.load(data_file)

    return data


def write_JSON(filename, data):
    # Dump all the JSON in a file.
    obj = open(filename, 'wb')
    obj.write(str(data))
    obj.close


def write_fancy_JSON(filename, data):
    # Write json so that it is readable by humans (rowchange, indent..).
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, sort_keys = True, indent = 4, ensure_ascii=False)


def load_csv_as_dictlist(filename, delimit):
    # Load a file in csv (common in .gazedata) and return data in JSON suitable
    # for analysis.

    print("Loading csv-file " + filename)

    try:
        ifile = open(filename, "rb")

    except Exception as ex:
        print("File loading error.")
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
