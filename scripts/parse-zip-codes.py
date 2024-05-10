#!/usr/bin/env python3

"""
format:

country code      : iso country code, 2 characters
postal code       : varchar(20)
place name        : varchar(180)
admin name1       : 1. order subdivision (state) varchar(100)
admin code1       : 1. order subdivision (state) varchar(20)
admin name2       : 2. order subdivision (county/province) varchar(100)
admin code2       : 2. order subdivision (county/province) varchar(20)
admin name3       : 3. order subdivision (community) varchar(100)
admin code3       : 3. order subdivision (community) varchar(20)
latitude          : estimated latitude (wgs84)
longitude         : estimated longitude (wgs84)
accuracy          : accuracy of lat/lng from 1=estimated, 4=geonameid, 6=centroid of addresses or shape
"""

from pathlib import Path

DATA = "data/zip-codes.txt"

communes = set()

count = 0
for line in Path(DATA).open():
    t = line.strip().split("\t")
    if t[0] != "FR":
        continue

    zip_code = t[1]
    if "CEDEX" in zip_code:
        continue

    communes.add(t[7])
    print(t)
    count += 1


print(f"count: {count}")
print(f"communes: {len(communes)}")
