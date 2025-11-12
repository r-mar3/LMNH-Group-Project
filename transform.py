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
        self.column_id = column_id
        self.column_names = column_names
        self.filename = filename

    def create_data_dict(self):
        return {column_name: [] for column_name in self.column_names}

    def transform(self) -> None:
        df = pd.DataFrame(self.data, columns=self.column_names)
        df.to_csv(self.filename, index_label=self.column_id)


class CountryTable(Entity):
    def __init__(self, data: list[dict]) -> None:
        super().__init__(data, 'country_id', [
            'country_name'], f'{OUTPUT_FOLDER}country.csv')

    def add_countries(self) -> None:
        """Add country to self"""
        countries = self.create_data_dict()

        for plant in self.data:
            origin_data = plant.get('origin_location')
            if origin_data:
                country_name = origin_data.get('country')
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
        cities = self.create_data_dict()

        for plant in self.data:
            origin_data = plant.get('origin_location')
            if origin_data:
                city_name = origin_data.get('city')
                country_name = origin_data.get('country')
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
        origins = self.create_data_dict()

        for plant in self.data:
            origin_data = plant.get('origin_location')
            if origin_data:
                longitude = origin_data.get('longitude')
                latitude = origin_data.get('latitude')
                origins['longitude'].append(longitude)
                origins['latitude'].append(latitude)
                city_name = origin_data.get('city')

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
        botanists = self.create_data_dict()

        for plant in self.data:
            botanist_data = plant.get('botanist')
            if botanist_data:
                name = botanist_data.get('name')
                email = botanist_data.get('email')
                phone = botanist_data.get('phone')
                botanists['name'].append(name)
                botanists['email'].append(email)
                botanists['phone'].append(phone)

        self.data = botanists

    def transform(self):
        self.add_botanists()
        return super().transform()


class LicenseTable(Entity):
    def __init__(self, data: list[dict]):
        super().__init__(data, 'license_id', [
            'license_number', 'license_name', 'license_url'], f'{OUTPUT_FOLDER}license.csv')

    def add_licenses(self):
        licenses = self.create_data_dict()
        for plant in self.data:
            image_data = plant.get('images')
            if image_data:
                license_number = image_data.get('license')
                license_name = image_data.get('license_name')
                license_url = image_data.get('license_url')
                licenses['license_number'].append(license_number)
                licenses['license_name'].append(license_name)
                licenses['license_url'].append(license_url)

        self.data = licenses

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
        images = self.create_data_dict()
        for plant in self.data:
            image_data = plant.get('images')
            if image_data:
                original_url = image_data.get('original_url')
                regular_url = image_data.get('regular_url')
                medium_url = image_data.get('medium_url')
                small_url = image_data.get('small_url')
                thumbnail = image_data.get('thumbnail')
                images['original_url'].append(original_url)
                images['regular_url'].append(regular_url)
                images['medium_url'].append(medium_url)
                images['small_url'].append(small_url)
                images['thumbnail'].append(thumbnail)

                license_number = image_data.get('license_number')
                if license_number in self.licenses:
                    license_id = self.licenses.data.index(license_number)
                    images['license_id'].append(license_id)

        self.data = images

    def transform(self):
        self.add_images()
        return super().transform()


class SpeciesTable(Entity):
    def __init__(self, data: list[dict], images: ImageTable):
        super().__init__(data, 'species_id', [
            'name', 'scientific_name', 'image_id'], f'{OUTPUT_FOLDER}species.csv')
        self.images = images

    def add_species(self):
        species = self.create_data_dict()

        for plant in self.data:
            name = plant.get('name')
            scientific_name = plant.get('scientific_name')
            species['name'].append(name)
            species['scientific_name'].append(scientific_name)

            image_data = plant.get('images'):
            if image_data:
                original_url = image_data.get('original_url')
                image_id = self.images.data.index(original_url)
                species['image_id'].append(image_id)

            else:
                species['image_id'].append(None)

        self.data = species

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
