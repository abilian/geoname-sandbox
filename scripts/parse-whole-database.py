#!/usr/bin/env python3

"""
The main 'geoname' table has the following fields :
---------------------------------------------------
geonameid         : integer id of record in geonames database
name              : name of geographical point (utf8) varchar(200)
asciiname         : name of geographical point in plain ascii characters, varchar(200)
alternatenames    : alternatenames, comma separated, ascii names automatically transliterated, convenience attribute from alternatename table, varchar(10000)
latitude          : latitude in decimal degrees (wgs84)
longitude         : longitude in decimal degrees (wgs84)
feature class     : see http://www.geonames.org/export/codes.html, char(1)
feature code      : see http://www.geonames.org/export/codes.html, varchar(10)
country code      : ISO-3166 2-letter country code, 2 characters
cc2               : alternate country codes, comma separated, ISO-3166 2-letter country code, 200 characters
admin1 code       : fipscode (subject to change to iso code), see exceptions below, see file admin1Codes.txt for display names of this code; varchar(20)
admin2 code       : code for the second administrative division, a county in the US, see file admin2Codes.txt; varchar(80)
admin3 code       : code for third level administrative division, varchar(20)
admin4 code       : code for fourth level administrative division, varchar(20)
population        : bigint (8 byte int)
elevation         : in meters, integer
dem               : digital elevation model, srtm3 or gtopo30, average elevation of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in meters, integer. srtm processed by cgiar/ciat.
timezone          : the iana timezone id (see file timeZone.txt) varchar(40)
modification date : date of last modification in yyyy-MM-dd format


AdminCodes:
Most adm1 are FIPS codes. ISO codes are used for US, CH, BE and ME. UK and Greece are using an additional level between country and fips code. The code '00' stands for general features where no specific adm1 code is defined.
The corresponding admin feature is found with the same countrycode and adminX codes and the respective feature code ADMx.
"""
from dataclasses import dataclass
from pathlib import Path

DATA = "data/allCountries.txt"

communes = set()


@dataclass
class Geoname:
    geonameid: int
    name: str
    asciiname: str
    alternatenames: str
    latitude: float
    longitude: float
    feature_class: str
    feature_code: str
    country_code: str
    cc2: str
    admin1_code: str
    admin2_code: str
    admin3_code: str
    admin4_code: str
    population: int
    elevation: int
    dem: str
    timezone: str
    modification_date: str


count = 0
for line in Path(DATA).open():
    t = line.strip().split("\t")
    r = Geoname(*t)

    if r.country_code != "FR":
        continue

    if r.feature_class != "A":
        continue

    if "Paris" in r.name:
        print(r)
        print(r.feature_code, r.feature_class, r.name)

    count += 1

print(f"count: {count}")
