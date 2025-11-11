# pylint: disable=logging-fstring-interpolation
"""Script transform raw data, clean it, save it as csvs for each table"""
import json
import os
import pandas as pd
from pandas import DataFrame
from pprint import pprint

INPUT_FILE = './data/raw_data/plant_data_raw.json'
OUTPUT_FOLDER = './data//clean_data'


class Entity:
    def __init__(self, data: list[dict]) -> None:
        self.data = data

    def transform(self) -> pd.DataFrame:
        return pd.DataFrame(self.data)


class Country(Entity):
    def __init__(self, data: list[dict]) -> None:
        super().__init__(data)

    def transform(self) -> pd.DataFrame:

        return super().transform()


class City(Entity):
    def __init__(self, data: list[dict]) -> None:
        super().__init__(data)

    def transform(self) -> pd.DataFrame:
        return super().transform()


def setup_output() -> None:
    """Setup output folder for clean data"""
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)


def get_plants() -> list[dict]:
    """Gets plants from a file as a list of dicts"""
    with open(INPUT_FILE, 'rb') as f:
        # Parsing the JSON file into a Python dictionary
        data = json.load(f)
    return data


def add_country(country: Country, data: dict) -> None:
    """Create country dict"""
    countries = country.country_name

    name = data.get('origin_location')
    if name:
        name = name.get('country')

    if name and name not in countries:
        countries.append(name)


def normalise_into_tables(data: list[dict]):
    """Separate data into relevant tables"""
    country = Country()
    city_dict = {}
    origin_dict = {}
    reading_dict = {}
    plant_dict = {}
    species_dict = {}
    image_dict = {}
    license_dict = {}
    botanist_dict = {}

    for plant in data:
        add_country(country, plant)

    return country.country_name


if __name__ == "__main__":
    # setup_output()
    # plants = get_plants()
    # print(pd.DataFrame(normalise_into_tables(plants)))
