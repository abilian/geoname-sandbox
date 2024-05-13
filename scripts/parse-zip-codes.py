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
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from pycountry import countries

DATA = "data/zip-codes.txt"
RESULT = "data/all_zip_towns.json"
RESULT_ALPHA3_DIR = "data/towns"


def check_data_file_found():
    if Path(DATA).is_file():
        return
    print(f"{DATA} file not found:")
    print("Probably need to change path or download zip codes: ")
    print("https://download.geonames.org/export/zip/allCountries.zip")
    raise SystemExit(1)


@dataclass
class Town:
    country_code: str
    name: str
    zip_code: str
    # geonameid: int
    # feature_code: str


# def parse_country_codes() -> set:
#     cc_seen = set()
#     for line in Path(DATA).open():
#         splitted = line.strip().split("\t")
#         cc = splitted[0]
#         if cc:
#             cc_seen.add(cc)
#     return cc_seen
def save_json(results: dict):
    all_data = {}
    for key, val in results.items():
        all_data[key] = [asdict(item) for item in val]
    Path(RESULT).write_text(
        json.dumps(all_data, sort_keys=True, indent=4, ensure_ascii=False)
    )


def parse_cc_zip_town() -> list:
    check_data_file_found()
    towns_dict = {}
    for line in Path(DATA).open():
        t = line.strip().split("\t")
        if not t[0]:  # CC empty
            continue
        # remove zip code with spaces and second part (CEDEX, SP, ...))
        if len(t[1].split()) > 1:
            continue
        zip_code = t[1].strip()
        name_orig = t[2].strip()
        # filter towns names ending by numbers (like "Paris 10")
        name = re.sub(r"\d+$", "", name_orig).strip()
        t[2] = name
        key_id = (zip_code, name)
        towns_dict[key_id] = t  # for duplicates if any
    return list(towns_dict.values())


def split_cc(towns: list) -> dict:
    results = {}
    for t in towns:
        data = Town(t[0], t[2], t[1])
        if data.country_code not in results:
            results[data.country_code] = []
        results[data.country_code].append(asdict(data))
    return results


def export_as_splitted_files(towns_per_cc: dict):
    dest_dir = Path(RESULT_ALPHA3_DIR)
    dest_dir.mkdir(parents=True, exist_ok=True)
    # remove existing json files
    for path in dest_dir.glob("*.json"):
        path.unlink()
    # convert to alpha3 and export
    for cc, values in towns_per_cc.items():
        country = countries.get(alpha_2=cc)
        alpha_3 = country.alpha_3
        path = dest_dir / f"{alpha_3}.json"
        for item in values:
            del item["country_code"]
        path.write_text(
            json.dumps(values, sort_keys=True, indent=4, ensure_ascii=False)
        )


def main():
    check_data_file_found()
    towns = parse_cc_zip_town()
    towns_per_cc = split_cc(towns)
    Path(RESULT).write_text(
        json.dumps(towns_per_cc, sort_keys=True, indent=4, ensure_ascii=False)
    )

    for key in sorted(towns_per_cc):
        print(f"{key}: {len(towns_per_cc[key])}")
    print("--------------")
    for item in towns_per_cc["FR"]:
        if item["name"] == "Paris":
            print(item)
    print("--------------")
    for item in towns_per_cc["FR"]:
        if item["zip_code"] == "15800":
            print(item)
    print("--------------")
    for item in towns_per_cc["IT"]:
        if item["name"] == "Murano":
            print(item)
    export_as_splitted_files(towns_per_cc)


if __name__ == "__main__":
    main()
