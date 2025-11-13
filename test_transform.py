"""Tests transform script edge cases, ideal and unideal behaviour"""
import json
import pytest
import pandas as pd
from transform import get_nested, flatten_data, load_data, clean_phone
from transform import clean_data, add_alerts, format_errors, setup_output


def test_get_nested_is_dict():
    """Asserts that if a dict is passed in the function, it returns
    the key as expected"""
    assert get_nested({'plant_id': 12, 'name': 'test plant'},
                      'plant_id', ) == 12
    assert get_nested({'plant_id': 31, 'name': 'test plant'},
                      'name', ) == 'test plant'


def test_get_nested_not_dict():
    """Asserts that if something that isn't a dict is passed in,
    it returns 'None' as expected"""
    assert get_nested('not a dict', 'plant') is None
    assert get_nested(['item_1', 'item_2'], 'plant') is None
    assert get_nested(('x', 'y'), 'plant') is None
    assert get_nested(3.14, 'plant') is None
    assert get_nested(17, 'plant') is None
    assert get_nested(None, 'plant') is None
    assert get_nested(True, 'plant') is None


def test_get_nested_no_key():
    """Asserts that 'None' is returned if there is no key found"""
    assert get_nested(
        {'plant_id': 45, 'name': 'test plant'}, 'city') is None


@pytest.fixture
def fake_data():
    """Creating fake data for tests"""
    return [
        {'plant_id': 11,
         'name': 'Fake Plant',
         'scientific_name': ['Very Fake Plant'],
         'origin_location': {'country': 'France',
                             'city': 'Lyon',
                             'latitude': 45.7,
                             'longitude': 4.8},
         'botanist': {'name': 'Crabby',
                      'email': 'crabby@fakegmail.com',
                      'phone': '+44 1234567890'},
         'images': {'original_url': 'http://example.com/fakeplant.jpg',
                    'license_number': '123445'},
         'soil_moisture': 0.66,
         'temperature': 22,
         'last_watered': '2025-11-13T10:00:00',
         'recording_taken': '2025-11-13T12:00:00',
         'error': None
         },
        {'plant_id': 12,
         'name': 'Fake Tree',
         'scientific_name': ['Very fAKE TREE'],
         'origin_location': {'country': 'USA',
                             'city': 'Memphis',
                             'latitude': 35.1,
                             'longitude': 90.0},
         'botanist': {'name': 'Pepper',
                      'email': 'pepper@fakegmail..com',
                      'phone': '+44 0987654321'},
         'images': {'original_url': 'http://example.com/faketree.jpg',
                    'license_number': None},
         'soil_moisture': 0.3,
         'temperature': 31,
         'last_watered': '2025-11-13T10:00:00',
         'recording_taken': '2025-11-13T12:00:00',
         'error': None
         }
    ]


def test_flatten_data_correct_types_returned(fake_data):
    """Asserts that a list of dicts is returned when flattening data"""
    flattened_data = flatten_data(fake_data)
    assert isinstance(flattened_data, list)
    assert isinstance(flattened_data[1], dict)


def test_flatten_data_returns_all_data(fake_data):
    """Asserts that all data is flattened"""
    flattened_data = flatten_data(fake_data)
    assert len(flattened_data) == 2


def test_flatten_data_missing_values_1(fake_data):
    """Asserts that the data is flattened correctly"""
    flattened_data = flatten_data(fake_data)
    first_row = flattened_data[0]
    assert first_row['botanist_phone'] == fake_data[0]['botanist']['phone']


def test_flatten_data_missing_values_2(fake_data):
    """Asserts that if there are missing values, they are replaced with 'None' in
    the table"""
    flattened_data = flatten_data(fake_data)
    first_row = flattened_data[1]
    assert first_row['image_thumbnail_url'] is None


def test_load_data(monkeypatch, tmp_path, fake_data):
    """Assert that load_data returns a pandas DataFrame as expected"""
    tmp_file = tmp_path / "fake_data.json"
    monkeypatch.setattr("transform.INPUT_PATH", tmp_file)

    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(fake_data, f)

    test_dataframe = load_data()
    assert isinstance(test_dataframe, pd.DataFrame)


def test_load_data_row_count(monkeypatch, tmp_path, fake_data):
    """Assert that the dataframe has the same number of rows as the data
    and nothing is being dropped"""
    tmp_file = tmp_path / "fake_data.json"
    monkeypatch.setattr("transform.INPUT_PATH", tmp_file)

    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(fake_data, f)

    test_dataframe = load_data()
    assert len(test_dataframe) == len(fake_data)


def test_load_data_all_columns_exist(monkeypatch, tmp_path, fake_data):
    """Asserts that all the columns from the original data file are also found in
    the pandas DataFrame"""

    tmp_file = tmp_path / "fake_data.json"
    monkeypatch.setattr("transform.INPUT_PATH", tmp_file)

    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(fake_data, f)

    expected_columns = [
        'plant_id', 'species_name', 'species_scientific_name', 'country_name',
        'city_name', 'origin_latitude', 'origin_longitude', 'image_original_url',
        'image_regular_url', 'image_medium_url', 'image_small_url',
        'image_thumbnail_url', 'license_number', 'license_name', 'license_url',
        'botanist_name', 'botanist_email', 'botanist_phone',
        'reading_last_watered', 'reading_time_taken', 'reading_soil_moisture',
        'reading_temperature', 'reading_error'
    ]

    test_dataframe = load_data()

    for column in expected_columns:
        assert column in test_dataframe.columns


def test_clean_phone_symbols_excodes_cleaned():
    """Asserts that phone numbers with symbols such as a plus-sign, dashes and brackets,
    as well as extension codes are cleaned properly"""
    df = pd.DataFrame({
        'botanist_phone': ['+44 123-456-7890',
                           '07971231234x55   ',
                           '(415) 867-3157',
                           '+1 (628) 688-6908X23']
    })

    df_cleaned = clean_phone(df)

    assert df_cleaned.loc[0, 'botanist_phone'] == '441234567890'
    assert df_cleaned.loc[1, 'botanist_phone'] == '07971231234 x55'
    assert df_cleaned.loc[2, 'botanist_phone'] == '4158673157'
    assert df_cleaned.loc[3, 'botanist_phone'] == '16286886908 x23'


@pytest.fixture
def fake_dataframe(fake_data):
    """Creates a fake dataframe from the fake data"""
    return pd.DataFrame(flatten_data(fake_data))


def test_clean_data_types_correct(fake_dataframe):
    """Asserts that all data is cleaned as expected"""
    cleaned_fake_dataframe = clean_data(fake_dataframe)
    assert cleaned_fake_dataframe['license_number'].dtype.name == 'Int64'
    assert cleaned_fake_dataframe['botanist_email'].iloc[1] == 'pepper@fakegmail.com'
    assert cleaned_fake_dataframe['species_name'].iloc[0] == 'Fake Plant'
    assert cleaned_fake_dataframe['species_scientific_name'].iloc[1] == 'Very Fake Tree'
    assert cleaned_fake_dataframe['city_name'].iloc[0] == 'Lyon'
    assert cleaned_fake_dataframe['reading_last_watered'].dtype.name == 'datetime64[ns]'
    assert cleaned_fake_dataframe['reading_time_taken'].dtype.name == 'datetime64[ns]'
    assert pd.isna(cleaned_fake_dataframe['license_number'].iloc[1])


def test_format_errors_reading_error_correct():
    """Asserts that the function returns 'False' in reading_error column
    if it is empty/'None', and 'True' in other cases"""
    pre_formatted_dataframe = pd.DataFrame({
        'reading_temperature': [22, 64, 18],
        'reading_error': [None, 'something happened here', 70]
    })

    formatted_dataframe = format_errors(pre_formatted_dataframe)

    assert formatted_dataframe.loc[0, 'reading_error'] is False
    assert formatted_dataframe.loc[1, 'reading_error'] is True
    assert formatted_dataframe.loc[2, 'reading_error'] is True


def test_add_alerts_expected_results():
    """Asserts that alerts are correctly assigned as expected"""
    pre_alerts_dataframe = pd.DataFrame({
        'reading_temperature': [100, 50, 11, 49],
        'reading_soil_moisture': [0.98, 0.5, 0.45, 0.14],
        'reading_error': [True, False, False, False]
    })

    alerts_dataframe = add_alerts(pre_alerts_dataframe)

    assert not alerts_dataframe.loc[0, 'reading_alert']
    assert not alerts_dataframe.loc[1, 'reading_alert']
    assert alerts_dataframe.loc[2, 'reading_alert']
    assert alerts_dataframe.loc[3, 'reading_alert']


def setup_output_creates_dir(monkeypatch, tmp_path):
    """Asserts that if the output folder doesn't exist, it is created"""
    test_output_dir = tmp_path / "test_output"
    monkeypatch.setattr("transform.OUTPUT_PATH", str(test_output_dir))

    assert not test_output_dir.exists()

    setup_output()

    assert test_output_dir.exists()
