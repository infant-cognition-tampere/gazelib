'''
igazelib: A low level library for analyzing gaze-data files provided usually
by eyetracker-devices.

Gaze data is expected to be in JSON-format such as list of datapoints with
similar dict storing the properties for each point.

Example:
  [{xcoordinate:0.4, ...}, {xcoordinate:0.5, ...}, ..., {xcoordinate:-1, ...}]

List elements are called "gazepoints", and dict keys as "keys".

gazelib-library is designed to be used with a script file that calls
the library functions to perform different analysis steps.

Created by researchers in Infant Cognition Lab,
University of Tampere, Finland
'''

indent = "  "


def median(lst):
    '''
    Return median of the list of numbers.
    '''
    # http://stackoverflow.com/a/24101534/638546
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2

    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1]) / 2.0


def mean(lst):
    '''
    Return mean of the list of numbers.
    '''
    # http://stackoverflow.com/a/7716358/638546
    return float(sum(lst)) / len(lst) if len(lst) > 0 else float('nan')


def first_gazepoints_by_time(data, time_key, timeunits, silent=True):
    '''
    Clip first rows from DATA before milliseconds count of time has passed
    '''

    if not silent:
        print("Picking first " + str(timeunits) +
              " timeunit gazepoints from data...")
        print(indent + "List contains " + str(len(data)) +
              " gazepoints before operation.")

    tk = time_key  # short alias
    start = int(data[0][tk])
    new_data = [gp.copy() for gp in data if timeunits > int(gp[tk]) - start]

    if not silent:
        print(indent + "List contains " + str(len(new_data)) +
              " gazepoints after operation.")

    return new_data


def first_gazepoints(data, gpcount, silent=True):
    '''
    Clip first rows from DATA before milliseconds count of time has passed
    '''

    if not silent:
        print("Picking first " + str(gpcount) + " gazepoints from data...")
        print(indent + "List contains " + str(len(data)) +
              " gazepoints before operation.")

    new_data = [gp.copy() for index, gp in enumerate(data) if index < gpcount]

    if not silent:
        print(indent + "List contains " + str(len(new_data)) +
              " gazepoints after operation.")

    return new_data


def gazepoints_after_time(data, time_key, timeunits, silent=True):
    '''
    Clip rows from DATA after [timeunits] count of time has passed
    '''

    if not silent:
        print("Picking gazepoints after " + str(timeunits) +
              " timeunits from data using TETTime...")
        print(indent + "List contains " + str(len(data)) +
              " gazepoints before operation.")

    tk = time_key  # short alias

    # find the time of the first datapoint of the list
    start = int(get_value(data, 0, tk))

    # generate a new list of datapoints
    new_data = [gp.copy() for gp in data if timeunits <= int(gp[tk]) - start]

    if not silent:
        print(indent + "List contains " + str(len(new_data)) +
              " gazepoints after operation.")

    return new_data


def gazepoints_containing_value(data, key, value_list, silent=True):
    '''
    return the rows that contain certain value
    '''

    if not silent:
        print("Picking gazepoints with values " + str(value_list) +
              " assosiated with key " + str(key))
        print(indent + "List contains " + str(len(data)) +
              " gazepoints before operation.")

    # check if input is really a list
    assert isinstance(value_list, list)

    # find gazepoints which contain the value
    gazepoints_found = [gp.copy() for gp in data if gp[key] in value_list]

    if not silent:
        print(indent + "Datamatrix contains " + str(len(gazepoints_found)) +
              " gazepoints.")

    return gazepoints_found


def gazepoints_not_containing_value(data, key, value_list, silent=True):
    '''
    return the rows that DO NOT contain certain value
    '''

    if not silent:
        print("Picking gazepoints without values " + str(value_list) +
              " assosiated with key " + str(key))
        print(indent + "List contains " + str(len(data)) + " gazepoints.")

    # check if input is really a list
    assert isinstance(value_list, list)

    # find rows which do not contain the value
    rows_found = [row for row in data if row[key] not in value_list]

    if not silent:
        print(indent + "List contains " + str(len(rows_found)) +
              " gazepoints.")

    return rows_found


def split_at_change_in_value(data, key, silent=True):
    '''
    Split one list to multiple lists. New list is started each time when
    value in the column changes from previous one. Omitted on the case of
    first element.
    '''

    # return list of lists
    if not silent:
        print("Splitting data when change in value for key: " + str(key))

    list_of_new_datas = []

    new_data = []
    previous_item = None

    # loop throught all gazepoints
    for gp in data:

        # if there is gazepoints before
        if previous_item is not None:

            # if previous item does not match the one we are processing
            if not previous_item == gp[key]:
                list_of_new_datas.append(new_data)
                new_data = []

        new_data.append(gp.copy())
        previous_item = gp[key]

    # append the last remaining clip when all looped
    list_of_new_datas.append(new_data)

    if not silent:
        print(indent + "Returning " + str(len(list_of_new_datas)) +
              " gazepoint lists.")

    return list_of_new_datas


def get_value(data, gazepoint, key):
    '''
    Returns a value from specific datapoint with specific key.
    '''

    return data[gazepoint][key]


def replace_value(data, key, value_to_replace, value, silent=True):
    '''
    replaces all values value_to_replace on key with value.
    '''

    if not silent:
        print("Replacing values for key:" + str(key) + " with value " +
              str(value_to_replace))

    vtr = value_to_replace
    new_values = [value if gp[key] == vtr else gp[key] for gp in data]
    new_data = add_key(data, key, new_values)

    if not silent:
        print(indent + "Done.")

    return new_data


def border_violation(data, aoi, xkey, ykey, valkey,
                     accepted_validities, silent=True):
    '''
    Return true if during-non valid perioid gaze has crossed aoi-border.
    '''

    if not silent:
        print("Calculating if a gaze moved over aoi border " +
              "during invalid data...")

    gaze_in_last_good = True
    gaze_okay_before = True

    for index, row in enumerate(data):
        # if accepted_validities.__contains__(row[valcol]):
        if row[valkey] in accepted_validities:
            # gaze okay
            gaze_okay = True
        else:
            # gaze not okay
            gaze_okay = False

        gaze_in = inside_aoi(aoi, row[xkey], row[ykey])

        if index > 0:
            if gaze_okay:
                if not gaze_okay_before and gaze_in != gaze_in_last_good:
                    if not silent:
                        print(indent + "Border violation detected.")
                    return True

                gaze_in_last_good = gaze_in

        gaze_okay_before = gaze_okay

    if not silent:
        print(indent + "No border violation detected.")

    return False


def inside_aoi(aoi, x, y):
    '''
    If coordinates are inside aoi, return true, otherwise false.
    Aoi is expected to be a dict with keys "x1", "x2", "y1", "y2".
    Aoi represents an rectangle with top-left corner at (x1, y1) and
    bottom-right corner at (x2, y2).
    '''

    if aoi["x1"] < x and x < aoi["x2"] and aoi["y1"] < y and y < aoi["y2"]:
        return True
    else:
        return False


def combine_coordinates(data, accepted_validities, rxkey, rykey, rvalkey,
                        lxkey, lykey, lvalkey, silent=True):
    '''
    Combine two coordinate-columns with third validity-column to one column.
    '''

    if not silent:
        print("Combining two columns...")

    x = []
    y = []
    val = []

    # loop all rows and collect x, y coordinates +
    # minimum validity value (assumed to be best)
    for row in data:
        x.append(mean_of_valid_values([row[rxkey], row[lxkey]],
                                      [row[rvalkey], row[lvalkey]],
                                      accepted_validities))
        y.append(mean_of_valid_values([row[rykey], row[lykey]],
                                      [row[rvalkey], row[lvalkey]],
                                      accepted_validities))
        val.append(min(int(row[rvalkey]), int(row[lvalkey])))

    if not silent:
        print(indent + "Done.")

    return x, y, val


def add_key(data, key, new_values):
    '''
    Adds a key to the datapoint-list. New_values must match in length to
    the column with keys.
    '''

    new_data = []
    for index, gp in enumerate(data):
        new_gp = gp.copy()       # use copy-method to not only affect pointer
        new_gp[key] = new_values[index]
        new_data.append(new_gp)

    return new_data


def get_key(data, key):
    '''
    Returns a list of values, from single key in the data-parameter.
    '''

    column = []
    for row in data:
        column.append(row[key])
    return column


def median_filter_data(data, winlen, key):
    '''
    Performs median filtering to the datapoints in the specified column on
    DATA-structure. Further information see help medianFilter.
    Column specifies the column to filter the data with.
    '''

    new_data = add_key(data, key, median_filter(get_key(data, key), winlen))

    return new_data


def median_filter(datapoints, winlen, silent=True):
    '''
    Performs median filtering to the datapoints with window-length winlen.
    Winlen must be an odd integer
    (window: sample-(winlen-1)/2..sample..sample+(winlen-1)/2.
    Endings of the sample are truncated by the first/last sample to achieve
    filtered trace of same length than the original.
    Here datapoints must contain numbers, otherwise an error is presented.
    '''

    datapoints = list(map(float, datapoints))

    if not silent:
        print("Performing median filtering with window-length " +
              str(winlen) + " for " + str(len(datapoints)) + " datapoints...")

    # calculate padding length
    padlen = (winlen - 1) // 2

    # form padding (first and last number repeated at the beginning and end)
    pad_start = padlen * [datapoints[0]]
    pad_end = padlen * [datapoints[-1]]

    datapoints_pad = pad_start + datapoints + pad_end

    # for each datapoint
    filtered_datapoints = []
    for i in range(0, len(datapoints)):
        wind = datapoints_pad[i:i+2*padlen+1]
        filtered_datapoints.append(median(wind))

    if not silent:
        print(indent + "Done.")

    return filtered_datapoints


def interpolate_using_last_good_value(data, key, valkey, accepted_validities,
                                      silent=True):
    '''
    Interpolates values with key "key" in DATA-matrix by replacing the bad
    value with last good value before bad values (if there is at least one good
    value, otherwise, do nothing). Validitycolumn contains the validity
    markings for each datapoint and good validities are defined by the accepted
    validities-parameter. If the beginning of a trail is "bad", use the first
    appearing good value to interpolate that.
    '''

    if not silent:
        print("Interpolating values + " + key +
              ": using last good (or first good) value...")

    # find the first non-bad, if any

    first_valid = -1
    for gpnum, gp in enumerate(data):

        if gp[valkey] in accepted_validities and first_valid == -1:
            first_valid = gpnum

    # there was at least one good value
    if first_valid == -1:
        # if not, return data as it was
        if not silent:
            print(indent + "Done. No good data available")
        return data

    new_data = []

    last_non_bad = get_value(data, first_valid, key)
    for gp in data:
        if gp[valkey] in accepted_validities:
            # valid data
            last_non_bad = gp[key]
        else:
            gp[key] = last_non_bad

        new_data.append(gp)

    if not silent:
        print(indent + "Done.")

    return new_data


def gaze_inside_aoi(data, xcol, ycol, aoi, firstorlast, silent=True):
    '''
    Finds either the first row when gaze enters aoi or last.
    If gaze does not enter aoi, return -1
    '''

    if not silent:
        print("Calculating when gaze inside aoi: " + str(aoi) +
              " " + firstorlast + "time...")

    last_in = -1
    for rownumber, row in enumerate(data):
        if inside_aoi(aoi, row[xcol], row[ycol]):
            if firstorlast == "first":
                if not silent:
                    print(indent + "Done.")
                return rownumber

            last_in = rownumber

    if not silent:
        print(indent + "Done.")

    return last_in


def gaze_inside_aoi_percentage(data, xcol, ycol, aoi, silent=True):
    '''
    Calculate the percentage of gaze inside aoi borders on given data.
    '''

    if not silent:
        print("Calculating when the portion of gaze inside aoi: " + str(aoi))

    rowcount = len(data)

    if rowcount == 0:
        return -1

    gaze_inside = 0
    for row in data:
        if inside_aoi(aoi, row[xcol], row[ycol]):
            gaze_inside = gaze_inside + 1

    if not silent:
        print(indent + "Done.")

    return gaze_inside / float(rowcount)


def longest_non_valid_streak(data, valkey, timekey, accepted_validities,
                             silent=True):
    '''Longest streak of invalid values'''

    if not silent:
        print("Calculating longest non-valid streak...")

    streak_started = None
    longest_streak = 0
    streak_on = False

    for gp in data:

        # check if ongoing streak and put to longest if is
        if streak_on:
            # Assert streak_started is set if streak_on
            streaklen = float(gp[timekey]) - float(streak_started)
            if streaklen > longest_streak:
                longest_streak = streaklen

        # test if this datapoint valid and start streak or end it
        valid = gp[valkey] in accepted_validities
        if valid:
            streak_on = False
        else:
            if not streak_on:
                streak_started = gp[timekey]
            streak_on = True

    if not silent:
        print(indent + "Done.")

    return longest_streak


def valid_gaze_percentage(data, valkey, accepted_validities):
    '''Calculates the percentage of valid gaze in data.'''

    if len(data) == 0:
        return -1

    valid = 0

    for gp in data:
        if gp[valkey] in accepted_validities:
            valid = valid + 1

    return float(valid) / float(len(data))


def duration(data, timekey):
    '''Returns the length of the data in time units.'''

    if len(data) == 0:
        return -1
    elif len(data) <= 1:
        return 0.0

    end_time = float(get_value(data, -1, timekey))
    start_time = float(get_value(data, 0, timekey))
    return end_time - start_time


def SRT_index(rtimes, max_rt, min_rt):
    '''Calculate SRT index (Leppanen et al.)'''

    SRTs = []

    for rtime in rtimes:
        SRTs.append(1 - (max_rt-rtime) / (max_rt-min_rt))

    return mean(SRTs)


def group(data, group_key, value_key):
    '''
    Groups a list of datapoint-dicts so that one of the keys is used as
    "grouping key" - according to this the values specified by "value key" are
    sorted to the dict containing lists.
    '''

    datas_by_group = {}
    for datapoint in data:

        group = datapoint[group_key]
        value = datapoint[value_key]

        # if already entry of this type of group_key in the dict
        if group in datas_by_group:
            datas_by_group[group].append(value)
        else:
            datas_by_group[group] = [value]

    return datas_by_group


def group_lists(datas, group_key):
    '''
    Groups data by 0'th value in group_column and places each subset to a group
    defined by group_column.
    parameter: list of list of rows, grouping key
    value in datapoint[0][group_key] expected to exist
    '''

    datas_by_group = {}
    for data in datas:
        group = get_value(data, 0, group_key)

        # if already entry of this key in the
        if group in datas_by_group:
            datas_by_group[group] = datas_by_group[group] + data
        else:
            datas_by_group[group] = data

    return datas_by_group


def mean_of_valid_values(values, validities, accepted_validities):
    '''
    Returns mean of good validity tagged values. If none, returns -1.
    values: list, validities:list
    '''

    goodvalues = []

    for index, i in enumerate(values):
        if validities[index] in accepted_validities:
            goodvalues.append(float(i))

    if len(goodvalues) == 0:
            return -1
    else:
        return mean(goodvalues)
