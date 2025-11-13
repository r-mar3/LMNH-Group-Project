# pylint: disable=logging-fstring-interpolation
"""Script transform raw data, clean it, save it as csvs for each table"""
# TODO: Refactor data cleaning, probably a method in each class
# ensure all tables have correct data types
import json
import os
import pandas as pd
from pprint import pprint

INPUT_PATH = './data/raw_data/plant_data_raw.json'
OUTPUT_PATH = './data/new_clean_data/'


class TransformManager:
    """Main class"""

    def __init__(self, input_path: str, output_path) -> None:
        self.input_path = input_path
        self.output_path = output_path

    def load_data(self) -> pd.DataFrame:
        with open(self.input_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        return pd.DataFrame(self.flatten_data(raw_data))

    def get_nested(self, dictionary: dict, *keys: tuple):
        """Used to get data from a nested dict. Will return None if any level isn't valid"""

        for key in keys:
            if not isinstance(dictionary, dict):
                return None
            try:
                dictionary = dictionary.get(key)
            except KeyError:
                return None

        return dictionary

    def flatten_data(self, raw_data: list[dict]) -> list[dict]:
        """Flattens the input data into a full denormalised table"""
        rows = []
        for plant in raw_data:
            row = {
                'plant_id': plant.get('plant_id'),
                'species_name': plant.get('name'),
                'species_scientific_name': plant.get('scientific_name'),
                'country_name': self.get_nested(plant, 'origin_location', 'country'),
                'city_name': self.get_nested(plant, 'origin_location', 'city'),
                'origin_latitude': self.get_nested(plant, 'origin_location', 'latitude'),
                'origin_longitude': self.get_nested(plant, 'origin_location', 'longitude'),
                'image_original_url': self.get_nested(plant, 'images', 'original_url'),
                'image_regular_url': self.get_nested(plant, 'images', 'regular_url'),
                'image_medium_url': self.get_nested(plant, 'images', 'medium_url'),
                'image_small_url': self.get_nested(plant, 'images', 'small_url'),
                'image_thumbnail_url': self.get_nested(plant, 'images', 'thumbnail'),
                'license_number': self.get_nested(plant, 'images', 'license'),
                'license_name': self.get_nested(plant, 'images', 'license_name'),
                'license_url': self.get_nested(plant, 'images', 'license_url'),
                'botanist_name': self.get_nested(plant, 'botanist', 'name'),
                'botanist_email': self.get_nested(plant, 'botanist', 'email'),
                'botanist_phone': self.get_nested(plant, 'botanist', 'phone'),
                'reading_last_watered': plant.get('last_watered'),
                'reading_time_taken': plant.get('recording_taken'),
                'reading_soil_moisture': plant.get('soil_moisture'),
                'reading_temperature': plant.get('temperature')
            }
            if row.get('species_scientific_name'):
                row['species_scientific_name'] = row['species_scientific_name'][0]
            rows.append(row)

        return rows

    def transform(self) -> None:
        """Execute all transform processes"""
        df = self.load_data()

        countries = CountryTable(df)
        cities = CityTable(df, countries)
        licenses = LicenseTable(df)
        images = ImageTable(df, licenses)
        botanists = BotanistTable(df)
        species = SpeciesTable(df, images)
        origins = OriginTable(df, cities)
        plants = PlantTable(df, species, origins)
        readings = ReadingTable(df, botanists)

        for table in [countries, cities, licenses, images, botanists, species, origins, plants, readings]:
            table.clean_data()
            table.save_to_file()


class BaseTable:
    """Base class for all other tables"""

    def __init__(self, table_name: str, column_names: list[str]) -> None:
        self.table_name = table_name
        self.column_names = column_names
        self.data = pd.DataFrame(columns=column_names)

    def save_to_file(self) -> None:
        """Save the current table to a csv file"""
        self.data.to_csv(f'{OUTPUT_PATH}{self.table_name}.csv', index=False)

    def assign_ids(self, id_name: str) -> None:
        """Assign unique ids for each row in the data"""
        self.data.insert(0, id_name, range(1, len(self.data) + 1))

    def clean_data(self) -> None:
        pass


class CountryTable(BaseTable):
    def __init__(self, df: pd.DataFrame) -> None:
        super().__init__('country', ['country_name'])

        self.data = df[['country_name']].dropna().drop_duplicates()
        self.assign_ids('country_id')


class CityTable(BaseTable):
    def __init__(self, df: pd.DataFrame, countries: CountryTable) -> None:
        super().__init__('city', ['city_name', 'country_id'])

        cities = df[['city_name', 'country_name']].dropna().drop_duplicates()
        self.data = cities.merge(countries.data[['country_name', 'country_id']], on='country_name',
                                 how='left').drop(columns='country_name')
        self.assign_ids('city_id')


class LicenseTable(BaseTable):
    def __init__(self, df: pd.DataFrame) -> None:
        super().__init__('license', [
            'license_number', 'license_name', 'license_url'])

        licenses = df[['license_number',
                       'license_name', 'license_url']].dropna().drop_duplicates()
        licenses['license_number'] = licenses['license_number'].astype(int)
        self.data = licenses
        self.assign_ids('license_id')


class ImageTable(BaseTable):
    def __init__(self, df: pd.DataFrame, licenses: LicenseTable) -> None:
        super().__init__('image', ['image_original_url', 'image_regular_url',
                                   'image_medium_url', 'image_small_url', 'image_thumbnail', 'license_id'])

        images = df[['image_original_url', 'image_regular_url', 'image_medium_url',
                     'image_small_url', 'image_thumbnail_url', 'license_number']].dropna().drop_duplicates()
        self.data = images.merge(licenses.data[['license_number', 'license_id']], on='license_number',
                                 how='left').drop(columns=['license_number'])
        self.assign_ids('image_id')


class BotanistTable(BaseTable):
    def __init__(self, df: pd.DataFrame) -> None:
        super().__init__('botanist', [
            'botanist_name', 'botanist_email', 'botanist_phone'])

        botanists = df[['botanist_name', 'botanist_email',
                        'botanist_phone']].dropna().drop_duplicates()
        # botanists['botanist_email'] = botanists['botanist_email'].str.replace(
        #     '..', '.')
        self.data = botanists
        self.assign_ids('botanist_id')

    def clean_data(self) -> None:
        self.data['botanist_email'] = self.data['botanist_email'].str.replace(
            '..', '.')


class SpeciesTable(BaseTable):
    def __init__(self, df: pd.DataFrame, images: ImageTable):
        super().__init__('species', ['species_name',
                                     'species_scientific_name', 'image_id'])

        species = df[['species_name', 'species_scientific_name',
                      'image_original_url']].dropna().drop_duplicates()
        self.data = species.merge(images.data[['image_original_url', 'image_id']],
                                  on='image_original_url', how='left').drop(columns='image_original_url')
        self.assign_ids('species_id')


class OriginTable(BaseTable):
    def __init__(self, df: pd.DataFrame, cities: CityTable) -> None:
        super().__init__(
            'origin', ['origin_longitude', 'origin_latitude', 'city_id'])

        origins = df[['origin_longitude',
                      'origin_latitude', 'city_name']].dropna().drop_duplicates()
        self.data = origins.merge(cities.data[['city_name', 'city_id']], on='city_name',
                                  how='left').drop(columns='city_name')
        self.assign_ids('origin_id')


class PlantTable(BaseTable):
    def __init__(self, df: pd.DataFrame, species: SpeciesTable, origins: OriginTable) -> None:
        super().__init__('plant', ['plant_id', 'species_id', 'origin_id'])

        plants = df[['plant_id', 'species_scientific_name',
                     'origin_latitude', 'origin_longitude']].dropna().drop_duplicates()
        plants = plants.merge(species.data[['species_scientific_name', 'species_id']],
                              on='species_scientific_name', how='left').drop(columns='species_scientific_name').dropna()
        plants['species_id'] = plants['species_id'].astype(int)

        self.data = plants.merge(origins.data[['origin_latitude', 'origin_longitude', 'origin_id']],
                                 on=['origin_latitude', 'origin_longitude'],
                                 how='left').drop(columns=['origin_latitude', 'origin_longitude'])


class ReadingTable(BaseTable):
    def __init__(self, df: pd.DataFrame, botanists: BotanistTable) -> None:
        super().__init__('reading', [
            'reading_last_watered', 'reading_time_taken', 'reading_soil_moisture', 'reading_temperature', 'botanist_id', 'plant_id'])

        readings = df[['reading_last_watered', 'reading_time_taken',
                       'reading_soil_moisture', 'reading_temperature', 'botanist_email', 'plant_id']].dropna().drop_duplicates()
        readings = readings.merge(botanists.data[[
            'botanist_email', 'botanist_id']], on='botanist_email', how='left').drop(columns='botanist_email')
        self.data = readings
        self.assign_ids('reading_id')

    def clean_data(self) -> None:
        self.data['botanist_id'] = self.data['botanist_id'].astype('Int64')


def setup_output() -> None:
    """Setup output folder for clean data"""
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)


def get_data() -> list[dict]:
    """Returns a list of each plant entry as a dict"""
    with open(INPUT_PATH, 'rb') as f:
        return json.load(f)


if __name__ == "__main__":
    setup_output()
    transform_controller = TransformManager(INPUT_PATH, OUTPUT_PATH)
    transform_controller.transform()
