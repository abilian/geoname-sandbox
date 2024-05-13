#!/usr/bin/env python3

# rem: pour FR et DE, ADM4 = ville
# Pour Italie, il semble que le niveau ville + zipcode = ADM3, ...

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
import json
from dataclasses import asdict, dataclass
from pathlib import Path

DATA = "data/allCountries.txt"
RESULT = "data/all_towns.json"
communes = set()


def check_data_file_found():
    if Path(DATA).is_file():
        return
    print(f"{DATA} file not found:")
    print("Probably need to change path or download ")
    print("https://download.geonames.org/export/dump/allCountries.zip")
    raise SystemExit(1)


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


@dataclass
class Town:
    geonameid: int
    name: str
    feature_code: str
    country_code: str
    zip_code: str


def count_lines() -> int:
    count = 0
    for line in Path(DATA).open():
        count += 1
    return count


def parse_country_codes() -> set:
    cc_seen = set()
    for line in Path(DATA).open():
        splitted = line.strip().split("\t")
        cc = splitted[8]
        if cc:
            cc_seen.add(cc)
    return cc_seen


def parse_admin_level(codes: set, level: str = "ADM4") -> dict:
    cc_towns = {cc: [] for cc in codes}
    for line in Path(DATA).open():
        splitted = line.strip().split("\t")
        geo = Geoname(*splitted)

        if geo.country_code not in codes:
            continue

        # lowest administrative level:
        if geo.feature_code != level:
            continue

        # if "Bern" in geo.name:
        #     print(geo)
        #     print(
        #         geo.feature_code,
        #         geo.feature_class,
        #         geo.name,
        #         geo.admin3_code,
        #         geo.admin4_code,
        #     )
        #

        if geo.name == "Paris":
            print(geo)

        expected_zip = geo.admin4_code.strip()
        if not expected_zip:
            expected_zip = geo.admin3_code.strip()
        town = Town(
            geo.geonameid, geo.name, geo.feature_code, geo.country_code, expected_zip
        )
        cc_towns[town.country_code].append(town)
    return cc_towns


def show_stats(cc_towns: dict):
    lst = []
    empty = 0
    for key, val in cc_towns.items():
        if len(val) == 0:
            empty += 1
            continue
        lst.append(f"{key}: {len(val)}")
    lst.sort()
    print("\n".join(lst))
    print(f"Empty: {empty}")


def save_json(results: dict):
    all_data = {}
    for key, val in results.items():
        all_data[key] = [asdict(item) for item in val]
    Path(RESULT).write_text(
        json.dumps(all_data, sort_keys=True, indent=4, ensure_ascii=False)
    )


def main():
    check_data_file_found()
    # print(count_lines())
    # allow_cc = {"FR", "DE", "IT", "CH", "BE"}
    # allow_cc = {"IT"}
    # allow_cc = {"CH"}
    country_codes = parse_country_codes()
    print("nb countries:", len(country_codes))
    # start with lowest level
    results = parse_admin_level(country_codes, "ADM4")
    print("------------- ADM4 results")
    show_stats(results)

    redo_cc = {cc for cc in results if len(results[cc]) < 10}
    result_adm3 = parse_admin_level(redo_cc, "ADM3")
    print("------------- ADM3 results")
    show_stats(result_adm3)
    results.update(result_adm3)

    redo_cc = {cc for cc in results if len(results[cc]) < 10}
    result_adm2 = parse_admin_level(redo_cc, "ADM2")
    print("------------- ADM2 results")
    show_stats(result_adm2)
    results.update(result_adm2)
    print("------------- Final results")
    show_stats(results)

    save_json(results)


# Bern sample:
# Geoname(geonameid='7285212', name='Bern/Berne/Berna', asciiname='Bern/Berne/Berna', alternatenames='Bern,Berna,Berne,CH0351',
# latitude='46.94761', longitude='7.40645', feature_class='A', feature_code='ADM3', country_code='CH', cc2='',
# admin1_code='BE', admin2_code='246', admin3_code='351', admin4_code='', population='134591', elevation='', dem='548',
# timezone='Europe/Zurich', modification_date='2021-12-03')
# ADM3 A Bern/Berne/Berna 351

# Paris
# Geoname(geonameid='6455259', name='Paris', asciiname='Paris',
# alternatenames='75056,Paris', latitude='48.86', longitude='2.34444',
# feature_class='A', feature_code='ADM4', country_code='FR', cc2='',
# admin1_code='11', admin2_code='75', admin3_code='751',
# admin4_code='75056', population='2190327', elevation='', dem='54',
# timezone='Europe/Paris', modification_date='2019-03-23')


if __name__ == "__main__":
    main()
