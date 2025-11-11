import json
import pytest
from extract import fetch_data_by_id, save_to_json, extract_data


def test_fetch_data_by_id_body_type():
    assert isinstance(fetch_data_by_id(2), dict)


def test_fetch_data_by_id_failure_1():
    with pytest.raises(ValueError):
        fetch_data_by_id(51)


def test_fetch_data_by_id_failure_2():
    with pytest.raises(ValueError):
        fetch_data_by_id(0)


def test_save_to_json_contents_correct(monkeypatch, tmp_path):
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
    fake_data = []
    fake_output = tmp_path/'plant_data_raw_test.json'

    monkeypatch.setattr('extract.OUTPUT_FILE', str(fake_output))
    save_to_json(fake_data)

    with open(fake_output, 'r', encoding='utf-8') as f:
        fake_output_data = json.load(f)

    assert fake_output.exists()
    assert fake_output_data == []


def monkeypatch_fetch_data_by_id(id):
    """Fake fetch data function"""
    return {
        "status_code": 200,
        "body": {'plant_id': id,
                 'name': f'Test plant {id}',
                 'last_watered': '2025-11-10T13:08:03.000Z',
                 'soil_moisture': 24.3068870673953,
                 'recording_taken': '2025-11-11T12:13:14.038Z'
                 }
    }


def test_extract_data(monkeypatch, tmp_path):

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


def monkeypatch_fetch_data_by_id_some_errors(id):
    """Fake fetch function that raises error for plants with even id number"""
    if id % 2 == 0:
        raise ValueError
    return {
        "status_code": 200,
        "body": {'plant_id': id,
                 'name': f'Test plant {id}',
                 'last_watered': '2025-11-10T13:08:03.000Z',
                 'soil_moisture': 24.3068870673953,
                 'recording_taken': '2025-11-11T12:13:14.038Z'
                 }
    }


def test_extract_data_some_errors(monkeypatch, tmp_path):
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
