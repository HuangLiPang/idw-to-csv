# Name
**idw.py<i></i>** — IDW to CSV

## Synopsis
python **idw.<i></i>py** \[options] \[_filename_]  
python **idw.<i></i>py** \[-h|--help|-v|--version]

## Description

Interpolating station values by IDW algorithm and save to csv file.

## Prerequisites

* python 3.6
* numpy  1.16.4

## Options
#### --version 
show program's version number and exit

#### -h, --help
show this help message and exit

### IDW Options:

#### -r RANGE, --range=RANGE
the effective range of AirBox in KM, default=10

#### -f EXP_FACTOR, --exp-factor=EXP_FACTOR
the exponential factor of IDW, default=2

### Coordinate Options:
#### -p PRECISION, --precision=PRECISION
the resolution of interpolation, default=1000

#### -b LAT_MAX LAT_MIN LON_MAX LON_MIN, --boundary=LAT_MAX LAT_MIN LON_MAX LON_MIN
the boundary of latitude and longitude, accuracy to 1 decimal place, default=26.0 21.0 123.0 119.0

#### -l AVERAGE_LATITUDE, --average-latitude=AVERAGE_LATITUDE
average latitude for calculating km in lat and lon,
                        default=23.5

## Bugs
See GitHub Issues: <https://github.com/HuangLiPang/idw-to-csv/issues>
