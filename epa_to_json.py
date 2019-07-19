#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Jul 16 2019

@author: huanglipang
"""

import json, os, sys
from optparse import OptionParser, OptionGroup

def main(argv):
  # https://docs.python.org/3.1/library/optparse.html#reference-guide
  parser = OptionParser(usage="usage: %prog [options] filename",
                        version="%prog 1.0")
  pathGroup = OptionGroup(parser, "Path Options")
  pathGroup.add_option("-e", "--epa-station-info",
                    action="store",
                    type="string",
                    dest="epa_station_info",
                    default="./epa_station.json",
                    metavar="EPA_STATION_INFO",
                    help="path of epa station info, default='./epa_station.json'")
  pathGroup.add_option("-d", "--output-directory",
                    action="store",
                    type="string",
                    dest="out_dir",
                    metavar="OUT_DIR",
                    help="output directory")
  parser.add_option_group(pathGroup)

  (options, args) = parser.parse_args()

  if len(args) != 1:
    parser.error("wrong number of arguments.")

  data = None
  epaInfo = None
  try:
    with open(args[0],'r') as f:
      content = f.read()
      content = '{"data":' + content + '}' 
      data = json.loads(content)
  except EnvironmentError as err:
    print("[ERROR]: load %s error." % options.args[0])
    print(err)

  try:
    with open(options.epa_station_info,'r') as f:
      epaInfo = json.load(f)
  except EnvironmentError as err:
    print("[ERROR]: load %s error." % options.epa_station_info)
    print(err)

  # Create target Directory if don't exist
  try:
    os.mkdir(options.out_dir)
    print("directory %s Created" % options.out_dir)
  except FileExistsError as err:
    print("[ERROR]: mkdir %s error." % options.out_dir) 
    print(err)

  area = ""
  while len(data["data"]):
    if area != data["data"][0]["device_id"]:
      area = data["data"][0]["device_id"]
      data[area] = []
    data["data"][0].pop("device_id")
    data[area].append(data["data"][0])
    data["data"].pop(0)
  data.pop("data")

  for i in range(len(data[area])):
    result = {"date": "", "feeds": []}
    result["date"] = data[area][i]["Date"]
    for station in data:
      result["feeds"].append({
          "c_d0": data[station][i]["PM2.5"],
          "gps_lat": epaInfo[station]["gps_lat"],
          "gps_lon": epaInfo[station]["gps_lon"]})
    outfilename = "./%s/epa_%s.json" % (options.out_dir, data[area][i]["Date"])
    try:
      with open(outfilename,'w+') as f:
        json.dump(result, f)
    except EnvironmentError as err:
      print("[ERROR]: save %s error." % outfilename)
      print(err)

    print("epa data to json complete")

if __name__ == "__main__":
  main(sys.argv[1:])