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
    def __init__(self, data: list[dict]) -> None:
        self.data = data
        self.column_id = 'id'
        self.column_names = ['entity']
        self.filename = 'entity.csv'

    def save_file(self) -> None:
        df = pd.DataFrame(self.data, columns=self.column_names)
        df.to_csv(self.filename, index_label=self.column_id)

    def transform(self) -> None:
        self.save_file()


class CountryTable(Entity):
    def __init__(self, data: list[dict]) -> None:
        super().__init__(data)
        self.column_names = ['country_name']
        self.column_id = 'country_id'
        self.filename = f'{OUTPUT_FOLDER}country.csv'

    def add_countries(self) -> None:
        """Add country to self"""
        countries = []

        for plant in self.data:
            origin = plant.get('origin_location')
            if origin:
                # only one value in values in this case
                values = origin.get('country')
            else:
                values = None

            if values and values not in countries:  # ensure unique
                countries.append(values)

        self.data = countries

    def transform(self) -> None:
        self.add_countries()
        super().transform()


class CityTable(Entity):
    def __init__(self, data: list[dict], countries: CountryTable) -> None:
        super().__init__(data)
        self.countries = countries
        self.column_names = ['city_name', 'country_id']
        self.column_id = 'city_id'
        self.filename = f'{OUTPUT_FOLDER}city.csv'

    def add_cities(self) -> None:
        """Add city to self"""
        cities = {'city_name': [], 'country_id': []}

        for plant in self.data:
            origin = plant.get('origin_location')
            if origin:
                city_name = origin.get('city')
                country_name = origin.get('country')

                # check to add to dict
                if city_name not in cities['city_name']:
                    cities['city_name'].append(city_name)
                    country_id = countries.data.index(country_name)
                    cities['country_id'].append(country_id)

        self.data = cities

    def transform(self) -> None:
        self.add_cities()
        super().transform()


class OriginTable(Entity):
    # FINISH ME AAAAAAAAHHHHHHHH!!!!!!!
    def __init__(self, data: list[dict], cities: CityTable) -> None:
        super().__init__(data)
        self.countries = countries
        self.column_names = ['longitude', 'latitude', 'city_id']
        self.column_id = 'origin_id'
        self.filename = f'{OUTPUT_FOLDER}city.csv'

    def add_cities(self) -> None:
        """Add city to self"""
        cities = {'city_name': [], 'country_id': []}

        for plant in self.data:
            origin = plant.get('origin_location')
            if origin:
                city_name = origin.get('city')
                country_name = origin.get('country')

                # check to add to dict
                if city_name not in cities['city_name']:
                    cities['city_name'].append(city_name)
                    country_id = countries.data.index(country_name)
                    cities['country_id'].append(country_id)

        self.data = cities

    def transform(self) -> None:
        self.add_cities()
        super().transform()


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
    plants = get_plants()
    countries = CountryTable(plants)
    countries.transform()
    cities = CityTable(plants, countries)
    cities.transform()
