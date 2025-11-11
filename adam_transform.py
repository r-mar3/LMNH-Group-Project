# pylint: disable=logging-fstring-interpolation
"""Script transform raw data, clean it, save it as csvs for each table"""
import json
import os
import pandas as pd
from pandas import DataFrame
from pprint import pprint

INPUT_FILE = './data/raw_data/plant_data_raw.json'
OUTPUT_FOLDER = './data//clean_data/'


class Entity:
    def __init__(self, data: list[dict], column_names: list[str], column_id: str) -> None:
        self.data = data
        self.column_names = []
        self.column_id = ''

    def save_file(self) -> None:
        df = pd.DataFrame(self.data, columns=self.column_names)
        df.to_csv(self.filename, index_label=self.column_id)

    def transform(self) -> None:
        self.save_file()


class Country(Entity):
    def __init__(self, data: list[dict]) -> None:
        super().__init__(data, ['country_id', 'country_name'], 'country_id')

    def transform(self) -> None:
        super().transform()


class City(Entity):
    def __init__(self, data: list[dict]) -> None:
        super().__init__(
            data, ['city_id', 'city_name', 'country_id'], 'city_id')

    def transform(self) -> None:
        super().transform()


class Origin(Entity):
    def __init__(self, data):
        super().__init__(
            data, ['origin_id', 'longitude', 'latitude', 'city_id'], 'city_id')

    def transform(self):
        return super().transform()


class Plant(Entity):
    def __init__(self, data):
        super().__init__(
            data, ['plant_id', 'species_id', 'origin_id'], 'plant_id')

    def transform(self):
        return super().transform()


class Botanist(Entity):
    def __init__(self, data, column_names, column_id):
        super().__init__(data, column_names, column_id)

    def transform(self):
        return super().transform()


class Image(Entity):
    def __init__(self, data, column_names, column_id):
        super().__init__(data, column_names, column_id)

    def transform(self):
        return super().transform()


class License(Entity):
    def __init__(self, data, column_names, column_id):
        super().__init__(data, column_names, column_id)

    def transform(self):
        return super().transform()


class Species(Entity):
    def __init__(self, data, column_names, column_id):
        super().__init__(data, column_names, column_id)

    def transform(self):
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


if __name__ == "__main__":
    setup_output()
