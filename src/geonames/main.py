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

from advanced_alchemy.base import BigIntBase
from advanced_alchemy.repository import SQLAlchemySyncRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import Mapped, sessionmaker, Session, mapped_column
from tqdm import tqdm

DATA = "data/zip-codes.txt"


class Place(BigIntBase):
    """
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

    __tablename__ = "geoname_place"  # type: ignore[assignment]
    country_code: Mapped[str] = mapped_column(index=True)
    postal_code: Mapped[str]
    place_name: Mapped[str]
    admin_name1: Mapped[str] = mapped_column(index=True)
    admin_code1: Mapped[str]
    admin_name2: Mapped[str] = mapped_column(index=True)
    admin_code2: Mapped[str]
    admin_name3: Mapped[str] = mapped_column(index=True)
    admin_code3: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]


class PlaceRepository(SQLAlchemySyncRepository[Place]):
    model_type = Place


engine = create_engine(
    "sqlite:///data/places.db",
    future=True,
)
session_factory: sessionmaker[Session] = sessionmaker(engine, expire_on_commit=False)


def check_data_file_found():
    if Path(DATA).is_file():
        return
    print(f"{DATA} file not found:")
    print("Probably need to change path or download ")
    print("https://download.geonames.org/export/zip/allCountries.zip")
    raise SystemExit(1)


def main():
    check_data_file_found()
    count = 0
    for line in Path(DATA).open():
        count += 1

    # Initializes the database.
    with engine.begin() as conn:
        Place.metadata.create_all(conn)

    with session_factory() as db_session, tqdm(total=count) as pbar:
        # 1) Load the JSON data into the US States table.
        repo = PlaceRepository(session=db_session)

        for line in Path(DATA).open():
            t = line.strip().split("\t")
            place = Place(
                country_code=t[0],
                postal_code=t[1],
                place_name=t[2],
                admin_name1=t[3],
                admin_code1=t[4],
                admin_name2=t[5],
                admin_code2=t[6],
                admin_name3=t[7],
                admin_code3=t[8],
                latitude=float(t[9]),
                longitude=float(t[10]),
                # accuracy=int(t[11]),
            )
            repo.add(place)

            if pbar.n % 10000 == 0:
                db_session.commit()

            pbar.update(1)

        db_session.commit()


if __name__ == "__main__":
    main()
