'''
Based on the National Hurricane Center's hurricane database format for a
specific date/time/location. This module is part of the Hurdat2FC repository
by Paul Schrum.

This module reads a hurricane track database (HURDAT2 from www.nhc.noaa.gov)
and creates a new shapefile from it. If the shapefile already exists,
this module overwrites it. (It destroys the file if it fails during write.)

The Coordinate System is WGS83 and can not be customized.

Usage:
python CreateHurricanePolylines.py <input file name> <output shapefile name>
'''

__author__ = 'Paul Schrum'

# To do List:
# 1. Create feature class (if path is gdb)
# 2. Store wind speed as z and barometric pressure as m.

import sys
if len(sys.argv) != 3:
    print("Failed to run because there are not enough arguments.")
    print()
    print("Usage:")
    print("python CreateHurricanePolylines.py <input file name> <out"
          "put shapefile name>")
    sys.exit(0)

import arcpy
import os

infile = sys.argv[1]
outfile = sys.argv[2]

if not os.path.exists(infile):
    if infile == 'Testing':
        infile = os.path.join(os.getcwd(), r"Test Data\hurdat2-2016-2018.txt")
    else:
        print("Can not find input file: {}".format(infile))
        print("No work performed. Exiting.")
        sys.exit(0)

if outfile == 'Testing':
    outfile = r'D:\Research\Datasets\Weather\Hurricanes\shapefiles' \
              r'\hurricanes.shp'

from HurricaneHistory import HurricaneHistory
history = HurricaneHistory(infile)

if not history:
    print("There was a problem loading the database file. Exiting.")
    sys.exit(0)

if arcpy.Exists(outfile):
    arcpy.Delete_management(outfile)

out_path, out_file_name = os.path.split(outfile)
av = [anSr for anSr in arcpy.ListSpatialReferences("*WGS*", "GCS")]
sr = arcpy.SpatialReference('Geographic Coordinate Systems/World/WGS 1984')
arcpy.CreateFeatureclass_management(out_path, out_file_name, "POLYLINE",
                                    None, "DISABLED", "DISABLED", sr)

designation = 'Designatio'
name = 'Name'
unique_name = 'UniqueName'
start_time = 'StartTime'
end_time = 'EndTime'
max_wind = 'MaxWind'
min_pressure = 'MinPressur'
shape = 'SHAPE@'

field_list = [designation, name, unique_name, start_time, end_time, max_wind,
              min_pressure, shape]

field_dict = {}
for idx, item in enumerate(field_list):
    field_dict[item] = idx

arcpy.AddField_management(outfile, field_name=designation,
        field_type='TEXT', field_length=15, field_is_nullable='NON_NULLABLE')
arcpy.AddField_management(outfile, field_name=name,
        field_type='TEXT', field_length=15, field_is_nullable='NON_NULLABLE')
arcpy.AddField_management(outfile, field_name=unique_name,
        field_type='TEXT', field_length=31, field_is_nullable='NON_NULLABLE')
arcpy.AddField_management(outfile, field_name=start_time,
        field_type='DATE', field_is_nullable='NON_NULLABLE')
arcpy.AddField_management(outfile, field_name=end_time,
        field_type='DATE', field_is_nullable='NON_NULLABLE')
arcpy.AddField_management(outfile, field_name=max_wind,
        field_type='SHORT')
arcpy.AddField_management(outfile, field_name=min_pressure,
        field_type='SHORT')

from HurricaneTrack import HurricaneTrack
from HurricaneRecord import HurricaneRecord

try:
    with arcpy.da.InsertCursor(outfile, field_list) as cursor:
        a_storm: HurricaneTrack
        for a_storm in history.all_storms.values():
            data_list = [None] * len(field_list)
            data_list[field_dict[designation]] = a_storm.designation
            data_list[field_dict[name]] = a_storm.name
            data_list[field_dict[unique_name]] = a_storm.unique_name
            data_list[field_dict[start_time]] = a_storm.start_time
            data_list[field_dict[end_time]] = a_storm.end_time
            data_list[field_dict[max_wind]] = a_storm.max_wind_speed
            data_list[field_dict[min_pressure]] = a_storm.min_bar_pressure
            line_points = [arcpy.Point(p[0], p[1]) for p in a_storm.shape]
            line_points = arcpy.Array(line_points)
            data_list[field_dict[shape]] = arcpy.Polyline(line_points)
            cursor.insertRow(data_list)

            dbg = True

finally:
    del cursor

dbg = True





