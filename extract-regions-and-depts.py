from pprint import pprint

from attr import frozen, field
from devtools import debug

COLUMNS_TXT = """
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
"""

COLUMNS = []
for line in COLUMNS_TXT.strip().split("\n"):
    column_name = line.split(":")[0].strip().replace(" ", "_")
    COLUMNS.append(column_name)


def safe_int(s):
    if s:
        return int(s)
    else:
        return 0


@frozen
class Record:
    geonameid: int = field(converter=int)
    name: str = field()
    asciiname: str = field()
    alternatenames: str = field()
    latitude: float = field(converter=float)
    longitude: float = field(converter=float)
    feature_class: str = field()
    feature_code: str = field()
    country_code: str = field()
    cc2: str = field()
    admin1_code: str = field()
    admin2_code: str = field()
    admin3_code: str = field()
    admin4_code: str = field()
    population: int = field(converter=safe_int)
    elevation: int = field(converter=safe_int)
    dem: str = field()
    timezone: str = field()
    modification_date: str = field()


records = []

for line in open("data/FR.txt"):
    record_dict = {}
    values = line.strip().split("\t")
    for column, value in zip(COLUMNS, values):
        record_dict[column] = value
    record = Record(**record_dict)
    records.append(record)


regions = {}
depts = {}
dept_to_region = {}

for record in records:
    if record.feature_code == "ADM2":
        depts[record.admin2_code] = record.name
        dept_to_region[record.admin2_code] = record.admin1_code
    if record.feature_code == "ADM1":
        regions[record.admin1_code] = record.name

# print("regions:")
# regions = sorted(regions.items())
# for code, name in regions:
#     print(code, name)
#
# print("depts:")
# depts = sorted(depts.items())
# for dept in depts:
#     print(dept)
#
# print("dept_to_region:")
# dept_to_region = sorted(dept_to_region.items())
# for dept, region in dept_to_region:
#     print(dept, "->", region)
#
# print(78 * "-")

print("dept_to_region = ", end="")
pprint(dept_to_region)

print("depts = ", end="")
pprint(depts)

print("regions = ", end="")
pprint(regions)
