# Igazelib: A low level library for analyzing gaze-data files.
# Gaze-data is expected to be in JSON-format such as list of 
# datapoints with dict storing the properties and
#  
#
# Library is designed to be used with a script file 
# that calls igazelib to perform different analysis steps.
#
# Created by researchers in Infant Cognition Lab, 
# University of Tampere, Finland

import csv
import numpy
import json

indent = "  "

############# technical functions ###############
def loadJSON(filename):
	# load json-type file

	with open(filename) as data_file:
		data = json.load(data_file)

	return data

def writeJSON(filename, data):
	obj = open(filename, 'wb')
	obj.write(str(data))
	obj.close

def writeFancyJSON(filename, data):
	with open(filename, 'w') as outfile:
		json.dump(data, outfile, sort_keys = True, indent = 4, ensure_ascii=False)


def loadCsvAsJSON(filename, delimit):
	# load the file and return data in usable form

	print "Loading csv-file " + filename

	try:
		ifile = open(filename, "rb")

	except Exception, ex:
		print "File loading error."
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

	print "File loaded succesfully. " + str(len(rows)) + " rows read."
	return rows

############# technical functions ###############

def firstRowsTime(data, time_key, timeunits):
	# Clip first rows from DATA before milliseconds count of time has passed

	print "Picking first " + str(timeunits) + " timeunit rows from data using TETTime..."
	print indent + "Datamatrix contains " + str(len(data)) + " rows before operation."

	starttime = int(data[0][time_key])
	new_data = [ row for row in data if timeunits>int(row[time_key])-starttime ]

	print indent + "Datamatrix contains " + str(len(new_data)) + " rows after operation."
	return new_data


def firstRows(data, rowcount):
	# Clip first rows from DATA before milliseconds count of time has passed

	print "Picking first " + str(rowcount) + " rows from data..."
	print indent + "Datamatrix contains " + str(len(data)) + " rows before operation."

	new_data = [ row for rowindex, row in enumerate(data) if  rowindex < rowcount]

	print indent + "Datamatrix contains " + str(len(new_data)) + " rows after operation."
	return new_data


def rowsAfterTime(data, time_key, timeunits):
	# Clip rows from DATA after milliseconds count of time has passed

	print "Picking rows after " + str(timeunits) + " timeunits from data using TETTime..."
	print indent + "Datamatrix contains " + str(len(data)) + " rows before operation."

	# find the time of the first datapoint of the list
	starttime = int(data[0][time_key])

	# generate a new list of datapoints 
	new_data = [ row for row in data if timeunits<=int(row[time_key])-starttime ]

	print indent + "Datamatrix contains " + str(len(new_data)) + " rows after operation."
	return new_data


def getRowsContainingValue(data, key, value_list):
	# return the rows that contain certain value

	print "Picking rows with values " + str(value_list) + " provided in column " + str(key)
	print indent + "Datamatrix contains " + str(len(data)) + " rows."

	# check if input is really a list
	assert isinstance(value_list, list)

	# find rows which contain the value
	rows_found = [ row for row in data if row[key] in value_list ]

	print indent + "Datamatrix contains " + str(len(rows_found)) + " rows."

	return rows_found


def getRowsNotContainingValue(data, key, value_list):
	# return the rows that DO NOT contain certain value

	print "Picking rows without values " + str(value_list) + " provided in column " + str(key)
	print indent + "Datamatrix contains " + str(len(data)) + " rows."

	# check if input is really a list
	assert isinstance(value_list, list)

	# find rows which do not contain the value
	rows_found = [ row for row in data if row[key] not in value_list  ]

	print indent + "Datamatrix contains " + str(len(rows_found)) + " rows."

	return rows_found


def clipAtChangeInValue(data, colnum):
	# Clip one list to multiple lists. New list is started each time when
	# value in the column changes from previous one. Omitted on the case of
	# first element.

	# return list of lists
	print "Clipping data when change in column: " + str(colnum)

	list_of_new_datas = []

	new_data = []
	for rownum, row in enumerate(data):
		if rownum > 0:
			if previous_item == row[colnum]:
				new_data.append(row)
			else:
				list_of_new_datas.append(new_data)
				new_data = []

		previous_item = row[colnum]

	print indent + "Returning " + str(len(list_of_new_datas)) + " dataclips."
	print indent + "Done."

	return list_of_new_datas


def getValue(data, row, key):
	# returns a value from row, column

	return data[row][key]


def replaceValue(data, colnum, value_to_replace, value):
	# replaces all values value_to_replace on column with value.

	print "Replacing values in column " + str(colnum) + " with value " + value_to_replace

	new_data = [value if row[colnum] == value_to_replace else row[colnum] for row in data]

	print indent + "Done."
	return new_data


def borderViolation(data, aoi, xcol, ycol, valcol, accepted_validities):
	# Return true if during-non valid perioid gaze has crossed aoi-border.

	print "Calculating if a gaze moved over aoi border during invalid data..."

	gaze_inside_last_good = True
	gaze_okay_before = True

	for index, row in enumerate(data):

	#	if accepted_validities.__contains__(row[valcol]):
		if row[valcol] in accepted_validities:
			# gaze okay
			gaze_okay = True
		else:
			# gaze not okay
			gaze_okay = False

		gaze_inside = insideAoi(aoi, row[xcol], row[ycol])

		if index > 0:
			if gaze_okay:
				if not gaze_okay_before and gaze_inside != gaze_inside_last_good:
					print indent + "Border violation detected."
					return True

				gaze_inside_last_good = gaze_inside

		gaze_okay_before = gaze_okay

	print indent + "No border violation detected."
	return False


def insideAoi(aoi, x, y):
	# if coordinates inside aoi, return true, otherwise false

	if (aoi["x1"] < x  and x < aoi["x2"]) and (aoi["y1"] < y and y < aoi["y2"]):
		return True
	else:
		return False


def combineEyes(data, accepted_validities, rxkey, rykey, rvalkey, lxkey, lykey, lvalkey):
	# Combine two coordinate-columns with third validity-column to one column

	print "Combining two columns..."

	x = []
	y = []
	val = []

	# loop all rows and collect x, y coordinates + minimum validity value (assumed to be best)
	for row in data:
		x.append(meanOfValidValues([row[rxkey], row[lxkey]], [row[rvalkey], row[lvalkey]], accepted_validities))
		y.append(meanOfValidValues([row[rykey], row[lykey]], [row[rvalkey], row[lvalkey]], accepted_validities))
		val.append(numpy.min([int(row[rvalkey]), int(row[lvalkey])]))

	print indent + "Done."
	return map(str, x), map(str, y), map(str, val)


def meanOfValidValues(values, validities, accepted_validities):
	# Returns mean of good validity tagged values. If none, returns -1.

	goodvalues = []

	for index, i in enumerate(values):
		if validities[index] in accepted_validities:
			goodvalues.append(float(i))

	if len(goodvalues) == 0:
			return -1
	else:
		return numpy.mean(goodvalues)


def addKey(data, column, key):

	print "Adding " + key + "-key to dataset.."

	new_data = []
	for index, row in enumerate(data):
		new_row = row
		new_row[key] = column[index]
		new_data.append(new_row)

	print indent + "Done"

	return new_data


def getColumn(data, colnum):

	print "Getting data from column " + str(colnum) + "..."

	column = []

	for row in data:
		column.append(row[colnum])

	print indent + "Done."

	return column


def replaceColumn(data, colnum, newcol):

	print "Replacing column " + str(colnum) + " with new column..."

	new_data = []
	for rownum, row in enumerate(data):
		row[colnum] = newcol[rownum]
		new_data.append(row)

	print indent + "Done."
	return new_data


def medianFilterData(data, winlen, key):
	# Performs median filtering to the datapoints in the specified column on
	# DATA-structure. Further information see help medianFilter.
	# Column specifies the column to filter the data with

	new_data = replaceColumn(data, key, medianFilter(getColumn(data, key), winlen))

	return new_data


def medianFilter(datapoints, winlen):
	# Performs median filtering to the datapoints with window-length winlen.
	# Winlen must be an odd integer
	# (window: sample-(winlen-1)/2..sample..sample+(winlen-1)/2.
	# Endings of the sample are truncated by the first/last sample to achieve
	# filtered trace of same length than the original.
	# Here datapoints must contain numbers, otherwise an error is presented.

	datapoints = map(float, datapoints)

	print "Performing median filtering with window-length " + str(winlen) + " for " + str(len(datapoints)) + " datapoints..."

	# calculate padding length
	padlen = (winlen-1)/2;

	# form padding (first and last number repeated at the beginning and end)
	pad_start = padlen * [datapoints[0]]
	pad_end = padlen * [datapoints[-1]]

	datapoints_pad = pad_start + datapoints + pad_end

	# for each datapoint
	filtered_datapoints = [];
	for i in range(0, len(datapoints)):
		wind = datapoints_pad[i:i+2*padlen+1]
		filtered_datapoints.append(numpy.median(wind))

	print indent + "Done."
	return filtered_datapoints


def interpolateUsingLastGoodValue(data, key, valcol, accepted_validities):
	# Interpolates values with key "key" in DATA-matrix by replacing the bad
	# value with last good value before bad values (if there is at least one good
	# value, otherwise, do nothing). Validitycolumn contains the validity markings
	# for each datapoint and good validities are defined by the accepted
	# validities-parameter. If the beginning of a trail is "bad", use the first
	# appearing good value to interpolate that.

	print "Interpolating values + " + key + ": using last good (or first good) value..."

	# find the first non-bad, if any

	firstrow = -1
	for rownum, row in enumerate(data):

		if row[valcol] in accepted_validities and firstrow == -1:
			firstrow = rownum

	# there was at least one good value
	if firstrow == -1:
		# if not, return data as it was
		print indent + "No good data available"
		print indent + "Done."
		return data

	new_data = []

	last_non_bad = data[firstrow][key]
	for row in data:
		if row[valcol] in accepted_validities:
			# valid data
			last_non_bad = row[key]
		else:
		    row[key] = last_non_bad

		new_data.append(row)

	print indent + "Done."
	return new_data


def gazeInsideAoi(data, xcol, ycol, aoi, firstorlast):
	# Finds either the first row when gaze enters aoi or last.
	# If gaze does not enter aoi, return -1

	print "Calculating when gaze inside aoi: " + str(aoi) + " " + firstorlast + "time..."

	last_in = -1
	for rownumber, row in enumerate(data):
		if insideAoi(aoi, row[xcol], row[ycol]):
			if firstorlast == "first":
				print indent + "Done."
				return rownumber

			last_in = rownumber

	print indent + "Done."

	return last_in


def gazeInsideAoiPercentage(data, xcol, ycol, aoi):
	# calculate the percentage of gaze inside aoi borders on given data.	

	print "Calculating when the portion of gaze inside aoi: " + str(aoi)

	rowcount = len(data)

	if rowcount == 0:
		return -1

	gaze_inside = 0
	for row in data:
		if insideAoi(aoi, row[xcol], row[ycol]):
			gaze_inside = gaze_inside + 1

	return gaze_inside/float(rowcount)

def longestNonValidStreak(data, valcol, timecol, accepted_validities):
	# Longest streak of non valid values

	longest_streak = 0
	streak_on = False

	for row in data:

		# check if ongoing streak and put to longest if is
		if streak_on:
			streaklen = float(row[timecol]) - float(streak_started)
			if streaklen > longest_streak:
				longest_streak = streaklen

		# test if this datapoint valid and start streak or end it
		valid = row[valcol] in accepted_validities
		if valid:
			streak_on = False
		else:
			if not streak_on:
				streak_started = row[timecol]
			streak_on = True

	return longest_streak


def validGazePercentage(data, valcol, accepted_validities):
	# Calculates the percentage of valid gaze in data.

	if len(data) == 0:
		return -1

	valid = 0
#	nonvalid = 0

	for row in data:
		if row[valcol] in accepted_validities:
			valid = valid + 1
#		else:
#			nonvalid = nonvalid + 1

	#return float(valid)/float(valid + nonvalid)
	return float(valid)/float(len(data))


def duration(data, timecol):
	# returns the length of the data in time units

	if len(data) == 0:
		return -1
	elif len(data) <= 1:
		return 0.0

	return float(getValue(data, -1, timecol)) - float(getValue(data, 0, timecol))


def SRT_index(rtimes, max_rt, min_rt):
	# calculate SRT index (Leppanen et al.)

	SRTs = []

	for rtime in rtimes:
		SRTs.append(1-(max_rt-rtime)/(max_rt-min_rt))


	return numpy.mean(SRTs)



