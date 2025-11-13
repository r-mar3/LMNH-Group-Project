"""Tests extract script edge cases, ideal and unideal behaviour"""
import json
import pytest
from extract import fetch_data_by_id, save_to_json, check_new_endpoints, extract_data, BASE_NUM_ENDPOINTS


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


def monkeypatch_fetch_data_by_id_1(id_num):
    """Fake fetch data function to ensure the new endpoint is only one increment
    above the current known endpoint"""
    if id_num == BASE_NUM_ENDPOINTS:
        return {"status_code": 200, "body": {"id": id_num}}
    return {"status_code": 404, "body": {}}


def test_check_new_endpoints_new_found(monkeypatch):
    """Asserts that if a new endpoint is found, the current_max_endpoint goes up
    by 5 during the search"""
    monkeypatch.setattr('extract.fetch_data_by_id',
                        monkeypatch_fetch_data_by_id_1)
    result = check_new_endpoints()
    assert result == BASE_NUM_ENDPOINTS + 5


def monkeypatch_fetch_data_by_id_2(id_num):
    """Fake fetch data function to ensure the new endpoint is only one increment
    above the current known endpoint"""
    return {"status_code": 404, "body": {}}


def test_check_new_endpoints_no_new_found(monkeypatch):
    """Asserts that if no new endpoint is found, the endpoint is equal to the
    base_num_endpoints value"""
    monkeypatch.setattr("extract.fetch_data_by_id",
                        monkeypatch_fetch_data_by_id_2)
    result = check_new_endpoints()
    assert result == BASE_NUM_ENDPOINTS


class FakePool:
    """Fake 'Pool' class to replace multiprocessing.Pool for tests"""

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def map(self, func, iterable):
        return [func(i) for i in iterable]


def monkeypatch_fetch_data_by_id_3(id_num):
    """Fake fetch data function"""
    return {"status_code": 200,
            "body": {'plant_id': id_num, 'name': f'Test plant {id_num}'}}


def test_extract_data(monkeypatch, tmp_path):
    """Tests the full functionality of the extract file if all plant data
    is successfully fetched and saved to .json file, and asserts that everything
    is working as expected"""
    import extract
    fake_output = tmp_path/'plant_data_raw_test.json'
    monkeypatch.setattr('extract.OUTPUT_FILE', str(fake_output))
    monkeypatch.setattr('extract.BASE_NUM_ENDPOINTS', 3)
    monkeypatch.setattr(extract.multiprocessing, "Pool",
                        lambda *a, **k: FakePool())
    monkeypatch.setattr(extract, 'check_new_endpoints', lambda: 3)
    monkeypatch.setattr(extract, "fetch_data_by_id",
                        monkeypatch_fetch_data_by_id_3)

    extract.extract_data()

    with open(fake_output, 'r', encoding='utf-8') as f:
        fake_output_data = json.load(f)

    ids = []
    names = []
    for datapoint in fake_output_data:
        ids.append(datapoint['plant_id'])
        names.append(datapoint['name'])

    assert len(fake_output_data) == 3
    assert ids == [1, 2, 3]
    assert names == ['Test plant 1', 'Test plant 2', 'Test plant 3']


def monkeypatch_fetch_data_by_id_some_errors(id_num):
    """Fake fetch function that raises error for plants with even id number"""
    if id_num % 2 == 0:
        return {"status_code": 404, "body": {}}
    return {"status_code": 200, "body": {"plant_id": id_num, "name": f"Test plant {id_num}"}}


def test_extract_data_some_errors(monkeypatch, tmp_path):
    """Tests the full functionality of the extract file if only some plant data
    is successfully fetched and saved to .json file, and asserts that everything
    is working as expected albeit the mixed success at fetching data"""
    import extract
    fake_output = tmp_path/'plant_data_raw_test.json'
    monkeypatch.setattr('extract.OUTPUT_FILE', str(fake_output))
    monkeypatch.setattr('extract.BASE_NUM_ENDPOINTS', 7)
    monkeypatch.setattr(extract.multiprocessing, "Pool",
                        lambda *a, **k: FakePool())
    monkeypatch.setattr(extract, 'check_new_endpoints', lambda: 7)
    extract.fetch_data_by_id = monkeypatch_fetch_data_by_id_some_errors

    extract.extract_data()

    with open(fake_output, 'r', encoding='utf-8') as f:
        fake_output_data = json.load(f)

        ids = []
        names = []
        for datapoint in fake_output_data:
            ids.append(datapoint['plant_id'])
            names.append(datapoint['name'])

        assert len(fake_output_data) == 4
        assert ids == [1, 3, 5, 7]
        assert names == ['Test plant 1', 'Test plant 3',
                         'Test plant 5', 'Test plant 7']
