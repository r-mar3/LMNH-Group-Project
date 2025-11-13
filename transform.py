# pylint: disable=logging-fstring-interpolation
"""Script transform raw data, clean it, save it as csvs for each table"""
import json
import os
import pandas as pd

INPUT_PATH = './data/raw_data/plant_data_raw.json'
OUTPUT_PATH = './data/'
OUTPUT_FILE = f'{OUTPUT_PATH}clean_data.csv'


def load_data() -> pd.DataFrame:
    """Returns a flatted (denormalised) dataframe of all data in the raw data csv"""
    with open(INPUT_PATH, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    return pd.DataFrame(flatten_data(raw_data))


def get_nested(dictionary: dict, *keys: tuple):
    """Used to get data from a nested dict. Will return None if any level isn't valid"""

    for key in keys:
        if not isinstance(dictionary, dict):
            return None
        try:
            dictionary = dictionary.get(key)
        except KeyError:
            return None

    return dictionary


def flatten_data(raw_data: list[dict]) -> list[dict]:
    """Flattens the input data into a full denormalised table"""
    rows = []
    for plant in raw_data:
        row = {
            'plant_id': plant.get('plant_id'),
            'species_name': plant.get('name'),
            'species_scientific_name': plant.get('scientific_name'),
            'country_name': get_nested(plant, 'origin_location', 'country'),
            'city_name': get_nested(plant, 'origin_location', 'city'),
            'origin_latitude': get_nested(plant, 'origin_location', 'latitude'),
            'origin_longitude': get_nested(plant, 'origin_location', 'longitude'),
            'image_original_url': get_nested(plant, 'images', 'original_url'),
            'image_regular_url': get_nested(plant, 'images', 'regular_url'),
            'image_medium_url': get_nested(plant, 'images', 'medium_url'),
            'image_small_url': get_nested(plant, 'images', 'small_url'),
            'image_thumbnail_url': get_nested(plant, 'images', 'thumbnail'),
            'license_number': get_nested(plant, 'images', 'license'),
            'license_name': get_nested(plant, 'images', 'license_name'),
            'license_url': get_nested(plant, 'images', 'license_url'),
            'botanist_name': get_nested(plant, 'botanist', 'name'),
            'botanist_email': get_nested(plant, 'botanist', 'email'),
            'botanist_phone': get_nested(plant, 'botanist', 'phone'),
            'reading_last_watered': plant.get('last_watered'),
            'reading_time_taken': plant.get('recording_taken'),
            'reading_soil_moisture': plant.get('soil_moisture'),
            'reading_temperature': plant.get('temperature'),
            'reading_error': plant.get('error')
        }
        if row.get('species_scientific_name'):
            row['species_scientific_name'] = row['species_scientific_name'][0]
        rows.append(row)

    return rows


def clean_phone(df: pd.DataFrame) -> pd.DataFrame:
    """Converts all phone numbers to symbol-less format, keeping extension codes"""
    df['botanist_phone'] = df['botanist_phone'].str.replace(
        r'[^0-9xX]', '', regex=True).str.replace(
        r'([xX])', ' x', regex=True).str.strip()

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Ensures values are of the correct type and format for their column"""
    df['license_number'] = df['license_number'].astype('Int64')
    df['botanist_email'] = df['botanist_email'].str.replace('..', '.')
    df['species_name'] = df['species_name'].str.title()
    df['species_scientific_name'] = df['species_scientific_name'].str.title()
    df['city_name'] = df['city_name'].str.title()
    df['reading_last_watered'] = pd.to_datetime(df['reading_last_watered'])
    df['reading_time_taken'] = pd.to_datetime(df['reading_time_taken'])

    df = clean_phone(df)

    return df


def add_alerts(data: pd.DataFrame) -> pd.DataFrame:
    """
    adding alerts column to dataframe based on if moisture
    or temperature is beyond 1 standard deviation of the 
    mean
    """

    temp_mean = data['reading_temperature'].mean()
    temp_stdev = data['reading_temperature'].std()

    moisture_mean = data['reading_soil_moisture'].mean()
    moisture_stdev = data['reading_soil_moisture'].std()

    data['reading_alert'] = (
        (~data['reading_error']) & (
            (data['reading_temperature'] > temp_mean+temp_stdev) |
            (data['reading_temperature'] < temp_mean-temp_stdev) |
            (data['reading_soil_moisture'] > moisture_mean+moisture_stdev) |
            (data['reading_soil_moisture'] < moisture_mean-moisture_stdev)
        )
    )
    return data


def format_errors(data: pd.DataFrame) -> pd.DataFrame:
    """
    formats the reading_error column so that it is True if there
    is an error and False if not
    """
    for i in range(len(data['reading_temperature'])):

        if pd.notna(data.loc[i, 'reading_error']):
            data.loc[i, 'reading_error'] = True
        else:
            data.loc[i, 'reading_error'] = False

    return data


def transform() -> None:
    """Execute all transform processes"""
    df = load_data()
    df = clean_data(df)
    df = format_errors(df)
    df = add_alerts(df)
    df.to_csv(OUTPUT_FILE, index=False)


def setup_output() -> None:
    """Setup output folder for clean data"""
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)


if __name__ == "__main__":
    setup_output()
    transform()
