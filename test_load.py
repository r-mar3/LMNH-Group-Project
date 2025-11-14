"""Tests load script to ensure script is working as expected"""
import pytest
import pandas as pd
from unittest.mock import MagicMock
from load import upload_table_data_with_foreign_key, upload_table_data


@pytest.fixture
def get_fake_conn_and_cursor():
    """Creates fake connection and cursor for tests"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_cursor, mock_conn


def test_upload_table_data_with_foreign_key_called_once(get_fake_conn_and_cursor):
    """Asserts that executemany is called once by the function"""
    fake_cursor, fake_connection = get_fake_conn_and_cursor

    fake_table_dict = {
        "table_name": "city",
        "columns": ["city_name", "country_id"],
        "unique_column": "city_name",
    }

    fake_dataframe = pd.DataFrame({"city_name": ["Seville"],
                                   "country_name": ["Spain"]})

    upload_table_data_with_foreign_key(
        fake_connection, fake_table_dict, fake_dataframe)

    fake_cursor.executemany.assert_called_once()


def test_upload_table_data_with_foreign_keys_correct_args(get_fake_conn_and_cursor):
    """Asserts that the args being passed when executed are as expected"""
    fake_cursor, fake_connection = get_fake_conn_and_cursor

    fake_table_dict = {
        "table_name": "city",
        "columns": ["city_name", "country_id"],
        "unique_column": "city_name",
    }

    fake_dataframe = pd.DataFrame({
        "city_name": ["Dale City", "New Clark"],
        "country_name": ["Moldova", "Moldova"]
    })

    upload_table_data_with_foreign_key(
        fake_connection, fake_table_dict, fake_dataframe)

    parameters = fake_cursor.executemany.call_args_list[0].args[1]
    expected_args = [("Dale City", "Moldova", "Dale City"),
                     ("New Clark", "Moldova", "New Clark")]

    assert parameters == expected_args


def test_upload_table_data_called_once(get_fake_conn_and_cursor):
    """Asserts that executemany is called once by the function"""
    fake_cursor, fake_connection = get_fake_conn_and_cursor

    fake_table_dict = {
        "table_name": "botanist",
        "columns": ["botanist_name", "botanist_email", "botanist_phone"],
        "unique_column": "botanist_email",
    }

    fake_dataframe = pd.DataFrame({
        "botanist_name": ["Pepper", "Crabby"],
        "botanist_email": ["pepper@fakegmail.com", "crabby@fakegmail.com"],
        "botanist_phone": ["1234567890", "0987654321"]
    })

    upload_table_data(fake_connection, fake_table_dict, fake_dataframe)

    fake_cursor.executemany.assert_called_once()


def test_upload_table_data_correct_args(get_fake_conn_and_cursor):
    """Asserts that the args being passed when executed are as expected"""
    fake_cursor, fake_connection = get_fake_conn_and_cursor

    fake_table_dict = {
        "table_name": "botanist",
        "columns": ["botanist_name", "botanist_email", "botanist_phone"],
        "unique_column": "botanist_email",
    }

    fake_dataframe = pd.DataFrame({
        "botanist_name": ["Pepper", "Crabby"],
        "botanist_email": ["pepper@fakegmail.com", "crabby@fakegmail.com"],
        "botanist_phone": ["1234567890", "0987654321"]
    })

    upload_table_data(fake_connection, fake_table_dict, fake_dataframe)

    params_used = fake_cursor.executemany.call_args_list[0].args[1]

    expected_params = [
        ("Pepper", "pepper@fakegmail.com", "1234567890", "pepper@fakegmail.com"),
        ("Crabby", "crabby@fakegmail.com", "0987654321", "crabby@fakegmail.com")
    ]

    assert params_used == expected_params
