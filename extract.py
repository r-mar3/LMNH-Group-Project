# pylint: disable=logging-fstring-interpolation
"""Script to extract data from the plants api and save to .json file"""
import json
import logging
import argparse
import os
import requests as req

BASE_URL = 'http://sigma-labs-bot.herokuapp.com/api/plants/'
OUTPUT_FOLDER = './data/raw_data/'
OUTPUT_FILE = f'{OUTPUT_FOLDER}plant_data_raw.json'
MAX_CONSECUTIVE_FAILURES = 10


def set_up_logging() -> None:
    """Configures logging based on --verbose flag"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Log extra information to console')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
        return

    logging.basicConfig(level=logging.ERROR)


def fetch_data_by_id(plant_id: int) -> dict:
    """Returns a dict with status code and response data"""
    response = req.get(f"{BASE_URL}{plant_id}", timeout=5)

    body = response.json()
    status_code = response.status_code
    if status_code == 404:
        raise ValueError

    return body


def save_to_json(data: list[dict]) -> None:
    """Saves list of dicts with plant data to a single json file"""
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def extract_data() -> None:
    """Runs the extract functions for all ids and catches error"""
    data = []
    consecutive_invalid_ids = 0
    current_id = 1
    while True:
        if consecutive_invalid_ids >= MAX_CONSECUTIVE_FAILURES:
            break
        try:
            data.append(fetch_data_by_id(current_id))
            consecutive_invalid_ids = 0
        except ValueError:
            logging.error(f"Plant with id '{current_id}' was not found")
            consecutive_invalid_ids += 1
        finally:
            current_id += 1

    save_to_json(data)


if __name__ == "__main__":
    set_up_logging()
    extract_data()
