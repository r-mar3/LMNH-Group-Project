from extract import fetch_data_by_id


def test_fetch_data_by_id_body_type():
    assert isinstance(fetch_data_by_id(2), dict)


def test_fetch_data_by_id_success():
    assert fetch_data_by_id(2)['status_code'] == 200
