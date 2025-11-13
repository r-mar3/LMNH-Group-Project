"""Tests extract script edge cases, ideal and unideal behaviour"""
import json
import pytest
from extract import fetch_data_by_id, save_to_json, extract_data


def test_fetch_data_by_id_body_type():
    """Asserts that the data fetched is returned as a dict"""
    assert isinstance(fetch_data_by_id(2), dict)


def test_save_to_json_contents_correct(monkeypatch, tmp_path):
    """Asserts that all the data fetched is saved into .json file"""
    fake_data = [{'plant_id': 55, 'name': 'Crabby Tree'},
                 {'plant_id': 56, 'name': 'Crabby Hedge'}]
    fake_output = tmp_path/'plant_data_raw_test.json'

    monkeypatch.setattr('extract.OUTPUT_FILE', str(fake_output))
    save_to_json(fake_data)

    with open(fake_output, 'r', encoding='utf-8') as f:
        fake_output_data = json.load(f)

    assert fake_output.exists()
    assert fake_output_data == fake_data


def test_save_to_json_empty(monkeypatch, tmp_path):
    """Asserts that if no data is fetched, an empty .json is created
    and nothing crashes"""
    fake_data = []
    fake_output = tmp_path/'plant_data_raw_test.json'

    monkeypatch.setattr('extract.OUTPUT_FILE', str(fake_output))
    save_to_json(fake_data)

    with open(fake_output, 'r', encoding='utf-8') as f:
        fake_output_data = json.load(f)

    assert fake_output.exists()
    assert fake_output_data == []


def monkeypatch_fetch_data_by_id(id_num):
    """Fake fetch data function"""
    return {
        "status_code": 200,
        "body": {'plant_id': id_num,
                 'name': f'Test plant {id_num}',
                 }
    }


def test_extract_data(monkeypatch, tmp_path):
    """Tests the full functionality of the extract file if all plant data
    is successfully fetched and saved to .json file, and asserts that everything
    is working as expected"""
    fake_output = tmp_path/'plant_data_raw_test.json'
    monkeypatch.setattr('extract.OUTPUT_FILE', str(fake_output))
    monkeypatch.setattr('extract.SEARCH_RANGE_MAX', 4)
    monkeypatch.setattr('extract.fetch_data_by_id',
                        monkeypatch_fetch_data_by_id)

    extract_data()

    with open(fake_output, 'r', encoding='utf-8') as f:
        fake_output_data = json.load(f)

    ids = []
    names = []
    for datapoint in fake_output_data:
        ids.append(datapoint['body']['plant_id'])
        names.append(datapoint['body']['name'])

    assert len(fake_output_data) == 3
    assert ids == [1, 2, 3]
    assert names == ['Test plant 1', 'Test plant 2', 'Test plant 3']


def monkeypatch_fetch_data_by_id_some_errors(id_num):
    """Fake fetch function that raises error for plants with even id number"""
    if id_num % 2 == 0:
        raise ValueError
    return {
        "status_code": 200,
        "body": {'plant_id': id_num,
                 'name': f'Test plant {id_num}',
                 }
    }


def test_extract_data_some_errors(monkeypatch, tmp_path):
    """Tests the full functionality of the extract file if only some plant data
    is successfully fetched and saved to .json file, and asserts that everything
    is working as expected albeit the mixed success at fetching data"""
    fake_output = tmp_path/'plant_data_raw_test.json'
    monkeypatch.setattr('extract.OUTPUT_FILE', str(fake_output))
    monkeypatch.setattr('extract.SEARCH_RANGE_MAX', 9)
    monkeypatch.setattr('extract.fetch_data_by_id',
                        monkeypatch_fetch_data_by_id_some_errors)

    extract_data()

    with open(fake_output, 'r', encoding='utf-8') as f:
        fake_output_data = json.load(f)

    ids = []
    names = []
    for datapoint in fake_output_data:
        ids.append(datapoint['body']['plant_id'])
        names.append(datapoint['body']['name'])

    assert len(fake_output_data) == 4
    assert ids == [1, 3, 5, 7]
    assert names == ['Test plant 1', 'Test plant 3',
                     'Test plant 5', 'Test plant 7']
