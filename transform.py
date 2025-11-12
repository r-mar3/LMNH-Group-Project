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
    def __init__(self, data: list[dict], column_id: str, column_names: list[str], filename: str) -> None:
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
        super().__init__(data, 'country_id', [
            'country_name'], f'{OUTPUT_FOLDER}country.csv')

    def add_countries(self) -> None:
        """Add country to self"""
        countries = {'country_name', []}

        for plant in self.data:
            origin = plant.get('origin_location')
            if origin:
                country_name = origin.get('country')
                countries['country_name'].append(country_name)

        self.data = countries

    def transform(self) -> None:
        self.add_countries()
        super().transform()


class CityTable(Entity):
    def __init__(self, data: list[dict], countries: CountryTable) -> None:
        super().__init__(data, 'city_id', [
            'city_name', 'country_id'], f'{OUTPUT_FOLDER}city.csv')
        self.countries = countries

    def add_cities(self) -> None:
        """Add city to self"""
        cities = {'city_name': [], 'country_id': []}

        for plant in self.data:
            origin = plant.get('origin_location')
            if origin:
                city_name = origin.get('city')
                country_name = origin.get('country')
                cities['city_name'].append(city_name)

                if country_name in self.countries['country_name']:
                    country_id = countries.data.index(country_name)
                    cities['country_id'].append(country_id)

        self.data = cities

    def transform(self) -> None:
        self.add_cities()
        super().transform()


class OriginTable(Entity):
    # FINISH ME AAAAAAAAHHHHHHHH!!!!!!!
    def __init__(self, data: list[dict], cities: CityTable) -> None:
        super().__init__(data, 'origin_id', [
            'longitude', 'latitude', 'city_id'], f'{OUTPUT_FOLDER}origin.csv')
        self.cities = cities

    def add_origins(self) -> None:
        """Add origin to self"""
        origins = {'longitude': [], 'latitude': [], 'city_id': []}

        for plant in self.data:
            origin = plant.get('origin_location')
            if origin:
                longitude = origin.get('longitude')
                latitude = origin.get('latitude')
                origins['longitude'].append(longitude)
                origins['latitude'].append(latitude)
                city_name = origin.get('city')

                if city_name in cities['city_name']:
                    city_id = cities.data.index(city_name)
                    origins['city_id'].append(city_id)

        self.data = origins

    def transform(self) -> None:
        self.add_origins()
        super().transform()


class BotanistTable(Entity):
    def __init__(self, data: list[dict]):
        super().__init__(data, 'botanist_id', [
            'name', 'email', 'phone'], f'{OUTPUT_FOLDER}botanist.csv')

    def add_botanists(self):
        # TODO: implement this
        pass

    def transform(self):
        self.add_botanists()
        return super().transform()


class LicenseTable(Entity):
    def __init__(self, data: list[dict]):
        super().__init__(data, 'license_id', [
            'license_number', 'license_name', 'license_url'], f'{OUTPUT_FOLDER}license.csv')

    def add_licenses(self):
        # TODO: implement this
        pass

    def transform(self):
        self.add_licenses()
        return super().transform()


class ImageTable(Entity):
    def __init__(self, data: list[dict], licenses: LicenseTable):
        super().__init__(data, 'image_id', [
            'original_url', 'regular_url',
            'medium_url', 'small_url',
            'thumbnail', 'license_id'], f'{OUTPUT_FOLDER}image.csv')
        self.licenses = licenses

    def add_images(self):
        # TODO: implement this
        pass

    def transform(self):
        self.add_images()
        return super().transform()


class SpeciesTable(Entity):
    def __init__(self, data: list[dict], images: ImageTable):
        super().__init__(data, 'species_id', [
            'name', 'scientific_name', 'image_id'], f'{OUTPUT_FOLDER}species.csv')
        self.images = images

    def add_species(self):
        # TODO: implement this
        pass

    def transform(self):
        self.add_species()
        return super().transform()


class PlantTable(Entity):
    def __init__(self, data: list[dict], species: SpeciesTable, origins: OriginTable):
        super().__init__(data, 'plant_id', [
            'species_id', 'origin_id'], f'{OUTPUT_FOLDER}license.csv')
        self.species = species
        self.origins = origins

    def add_licenses(self):
        # TODO: implement this
        pass

    def transform(self):
        self.add_plants()
        return super().transform()


class ReadingTable(Entity):
    def __init__(self, data: list[dict], botanists: BotanistTable, plants: PlantTable):
        super().__init__(data, 'reading_id', [
            'last_watered', 'recording_taken',
            'soil_moisture', 'temperature',
            'botanist_id', 'plant_id'], f'{OUTPUT_FOLDER}license.csv')
        self.botanists = botanists
        self.plants = plants

    def add_readings(self):
        # TODO: implement this
        pass

    def transform(self):
        self.add_readings()
        return super().transform()


def setup_output() -> None:
    """Setup output folder for clean data"""
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)


def get_data() -> list[dict]:
    """Gets plants from a file as a list of dicts"""
    with open(INPUT_FILE, 'rb') as f:
        # Parsing the JSON file into a Python dictionary
        data = json.load(f)
    return data


if __name__ == "__main__":
    setup_output()
    data = get_data()
    countries = CountryTable(data)
    countries.transform()
    # botanists = BotanistTable(plants)
    # botanists.transform()
    # licenses = LicenseTable(data)
    # licenses.transform()
    cities = CityTable(data, countries)
    cities.transform()
    origins = OriginTable(data, cities)
    origins.transform()
    # images = ImageTable(data, licences)
    # images.transform()
    # species = SpeciesTable(data, images)
    # species.transform()
    # plants = PlantTable(data, species, origins)
    # plants.transform()
    # readings = ReadingTable(data, plants, botanists)
    # readings.transform()
