#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on Jul 16 2019
@author: huanglipang
descriptions:
  Interpolating station values by IDW algorithm and save to csv file.

prerequisites:
  python 3.6
  numpy  1.16.4
"""

import sys, json, time, numpy
from math import sqrt, pow, log, floor, cos, pi
from optparse import OptionParser, OptionGroup

# input data format
'''
{
  "date":"2019-01-01",
  "feeds": [
    {
      "device_id": "AAA",
      "c_d0": 12, 
      "gps_lat": 23.23,
      "gps_lon": 123.23
    },
    {
      "device_id": "BBB",
      "c_d0": 23,
      "gps_lat": 24.24,
      "gps_lon": 124.24
    }
  ]
}
'''

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
  """
  Call in a loop to create terminal progress bar
  @params:
      iteration   - Required  : current iteration (Int)
      total       - Required  : total iterations (Int)
      prefix      - Optional  : prefix string (Str)
      suffix      - Optional  : suffix string (Str)
      decimals    - Optional  : positive number of decimals in percent complete (Int)
      length      - Optional  : character length of bar (Int)
      fill        - Optional  : bar fill character (Str)
  """
  percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
  filledLength = int(length * iteration // total)
  bar = fill * filledLength + '-' * (length - filledLength)
  print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
  # Print New Line on Complete
  if iteration == total: 
    print()

def openFile(dataPath):
  try:
    # loading data points [lat, lon, value]
    data = json.load(open(dataPath), parse_float=float)
    return data
  except Exception as err:
    print("[ERROR]: Load %s error." % dataPath)
    print(err)

def IDW(data, options, outFileName):
  # lat lon boundary
  BOUNDARY = {
    "lat": {
      "max": 26.0, "min": 21.0
    },
    "lon": {
      "max": 123.0, "min": 119
    }
  }
  # lat and lon's accuracy is 1 decimal place
  BOUNDARY["lat"]["max"] = float(floor(options.boundary[0] * 10)) / 10
  BOUNDARY["lat"]["min"] = float(floor(options.boundary[1] * 10)) / 10
  BOUNDARY["lon"]["max"] = float(floor(options.boundary[2] * 10)) / 10
  BOUNDARY["lon"]["min"] = float(floor(options.boundary[3] * 10)) / 10
  # BOUNDARY = {
  #   "lat": {"min": 21.0, "max": 26.0},
  #   "lon": {"min": 119.0, "max": 123.0}
  # }

  # PRIECISE of how many division in lenth, e.g. 10, 100, 1000 etc.
  PRECISION = options.precision
  LOG_PRECISION = int(log(PRECISION, 10)) + 1
  # effective range in KM
  EFFECTIVE_RANGE = options.range
  # exponential factor for calculating idw value
  EXP_FACTOR = options.exp_factor

  # grid size
  # a cell of 1 lat * 1 lon
  # length of 1 degree lon = 111.320 km
  # length of 1 degree lat = 110.574 km
  latToKm = 110.574
  # adjust the 1 degree longititude length
  lonToKm = 111.320 * cos(options.average_latitude * pi / 180);

  latDiff = BOUNDARY["lat"]["max"] - BOUNDARY["lat"]["min"]
  lonDiff = BOUNDARY["lon"]["max"] - BOUNDARY["lon"]["min"]

  lonCellLength = int(lonDiff * PRECISION)
  latCellLength = int(latDiff * PRECISION)
  print("boundary:")
  print("  latitude: %3.1f ~ %3.1f" % (BOUNDARY["lat"]["min"], BOUNDARY["lat"]["max"]))
  print("  longitude: %3.1f ~ %3.1f" % (BOUNDARY["lon"]["min"], BOUNDARY["lon"]["max"]))
  print("precision: %d, effective range: %d km" % (PRECISION, EFFECTIVE_RANGE))
  print("cells in lon: %d, cells in lat: %d\n" % (lonCellLength, latCellLength))
  # numpy.zeros returns a new array of given shape and type, filled with zeros.
  # cell[lat][lon]
  # cell summation numerator
  cellSN = numpy.zeros((latCellLength, lonCellLength),\
                       dtype=float, order='C')
  # cell summation denominator
  cellSD = numpy.zeros((latCellLength, lonCellLength),\
                       dtype=float, order='C')

  pm25Value = numpy.zeros((latCellLength, lonCellLength),\
                       dtype=float, order='C')
  
  progressBarLen = len(data["feeds"])
  print("IDW calculating start")
  print("calculating interpolation...")
  printProgressBar(0, progressBarLen, prefix = 'Progress:', suffix = 'Complete', length = 50)
  tStart = time.time()
  for progressIdx, point in enumerate(data["feeds"]):
    # point[lat][lon][value]
    # point is the center of the cell
    lat = round(point["gps_lat"], LOG_PRECISION)
    lon = round(point["gps_lon"], LOG_PRECISION)
    value = float(point["c_d0"])

    if(lat >= BOUNDARY["lat"]["min"] and lat < BOUNDARY["lat"]["max"] and \
       lon >= BOUNDARY["lon"]["min"] and lon < BOUNDARY["lon"]["max"]):
      
      # calculate boundary coordinate in cellSN and cellSD
      # boundary of cell in lat lon
      x1 = lon - EFFECTIVE_RANGE / lonToKm
      x2 = lon + EFFECTIVE_RANGE / lonToKm
      y1 = lat - EFFECTIVE_RANGE / latToKm
      y2 = lat + EFFECTIVE_RANGE / latToKm
      
      # boundary of cell in cellSN cellSD index
      x1 = int(round(x1 - BOUNDARY["lon"]["min"], LOG_PRECISION) * PRECISION)
      x2 = int(round(x2 - BOUNDARY["lon"]["min"], LOG_PRECISION) * PRECISION)
      y1 = int(round(y1 - BOUNDARY["lat"]["min"], LOG_PRECISION) * PRECISION)
      y2 = int(round(y2 - BOUNDARY["lat"]["min"], LOG_PRECISION) * PRECISION)
      
      # check x1, x2, y1, y2 in the index boundary
      if(x2 < 0):
        continue
      if(x1 >= lonCellLength):
        continue
      if(y2 < 0):
        continue
      if(y1 >= latCellLength):
        continue
      
      if(x1 < 0):
        x1 = 0
      if(x2 >= lonCellLength):
        x2 = lonCellLength - 1
      if(y1 < 0):
        y1 = 0
      if(y2 >= latCellLength):
        y2 = latCellLength - 1
      
      # transfer lat lon into index
      lat = int((lat - BOUNDARY["lat"]["min"]) * PRECISION)
      lon = int((lon - BOUNDARY["lon"]["min"]) * PRECISION)
      # set cell center values
      cellSN[lat][lon] = value
      cellSD[lat][lon] = -1
      
      # calculate idw
      # y represents latitude
      # x represents longitude
      for y in range(y1, y2):
        for x in range(x1, x2):
          if(cellSD[y][x] < 0.0):
            # center of the cell
            # which has real pm2.5 value
            # cellSD = -1
            continue
          
          # calculate distance
          distance = sqrt(pow(((x - lon) / PRECISION * lonToKm), 2) +\
                          pow(((y - lat) / PRECISION * latToKm), 2))
          if(distance > EFFECTIVE_RANGE):
            continue
          
          if distance > 0:
            distanceExp = pow(distance, EXP_FACTOR)
            cellSN[y][x] += value / distanceExp
            cellSD[y][x] += 1 / distanceExp
    printProgressBar(progressIdx + 1, progressBarLen, prefix = 'Progress:', suffix = 'Complete', length = 50)

  progressBarLen = latCellLength
  print("calculating cell value...")
  printProgressBar(0, progressBarLen, prefix = 'Progress:', suffix = 'Complete', length = 50)
  for y in range(0, latCellLength):
    for x in range(0, lonCellLength):
      if(cellSD[y][x] < 0):
        cellSD[y][x] = 1
      interpolateValue = 0
      if(cellSN[y][x] != 0):
        interpolateValue = cellSN[y][x] / cellSD[y][x]
      
      # calculate pm2.5 value
      pm25Value[y][x] = interpolateValue
    printProgressBar(y + 1, progressBarLen, prefix = 'Progress:', suffix = 'Complete', length = 50)
  tEnd = time.time()
  print("completing IDW used %f seconds\n" % (tEnd - tStart))
  

  tStart = time.time()
  print("saving the csv file...")
  # add longitude degrees as header
  csvHeader = ""
  interval = (BOUNDARY["lon"]["max"] - BOUNDARY["lon"]["min"]) / lonCellLength
  for i in range(lonCellLength):
    csvHeader = csvHeader + str(BOUNDARY["lon"]["min"] + interval * i) + ','

  # save csv
  # https://docs.scipy.org/doc/numpy/reference/generated/numpy.zeros.html
  numpy.savetxt(outFileName.replace(".json", ".csv"), 
                pm25Value, fmt="%.2f", delimiter=",", header=csvHeader, comments='')
  tEnd = time.time()
  print("saving file used %f seconds\n" % (tEnd - tStart))

def main(argv):
  # https://docs.python.org/3.1/library/optparse.html#reference-guide
  parser = OptionParser(usage="usage: %prog [options] filename",
                        version="%prog 1.0")
  idwGroup = OptionGroup(parser, "IDW Options")
  # add option to group
  # options
  idwGroup.add_option("-r", "--range",
                    action="store",
                    type="int",
                    # options.range
                    dest="range",
                    default=10,
                    metavar="RANGE",
                    help="the effective range of AirBox in KM, default=10")
  idwGroup.add_option("-f", "--exp-factor",
                    action="store",
                    type="int",
                    dest="exp_factor",
                    default=2,
                    metavar="EXP_FACTOR",
                    help="the exponential factor of IDW, default=2")
  coordinateGroup = OptionGroup(parser, "Coordinate Options")
  coordinateGroup.add_option("-p", "--precision",
                    action="store",
                    type="int",
                    dest="precision",
                    default=1000,
                    metavar="PRECISION",
                    help="the resolution of interpolation, default=1000")
  coordinateGroup.add_option("-b", "--boundary",
                    nargs=4,
                    action="store", # optional because action defaults to "store"
                    type="float",
                    dest="boundary",
                    default=(26.0, 21.0, 123.0, 119.0),
                    metavar="LAT_MAX LAT_MIN LON_MAX LON_MIN",
                    help="the boundary of latitude and longitude, accuracy to 1 decimal place, default=26.0 21.0 123.0 119.0")
  
  coordinateGroup.add_option("-l", "--average-latitude",
                    action="store",
                    type="float",
                    dest="average_latitude",
                    default=23.5,
                    metavar="AVERAGE_LATITUDE",
                    help="average latitude for calculating km in lat and lon, default=23.5")
  parser.add_option_group(idwGroup)
  parser.add_option_group(coordinateGroup)

  (options, args) = parser.parse_args()

  # args only contains the filename
  if len(args) != 1:
    parser.error("wrong number of arguments.")
  # check the boundary is valid or not
  if options.boundary[1] > options.boundary[0] or options.boundary[3] > options.boundary[2]:
    parser.error("invalid boundary.")

  data = openFile(args[0])
  IDW(data, options, args[0])

if __name__ == "__main__":
  main(sys.argv[1:])
