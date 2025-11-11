import requests as req
import json
import logging
import argparse

BASE_URL = 'http://sigma-labs-bot.herokuapp.com/api/plants/'
OUTPUT_FILE = './raw_data/plant_data_raw.json'


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


def fetch_data_by_id(id: int) -> dict:
    """Returns a dict with status code and response data"""
    response = req.get(f"{BASE_URL}{id}")

    body = response.json()
    status_code = response.status_code
    if status_code == 404:
        raise ValueError

    return {"status_code": status_code, "body": body}


def save_to_json(data: list[dict]) -> None:
    """Saves list of dicts with plant data to a single json file"""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def extract_data() -> None:
    """Runs the extract functions for all ids and catches error"""
    data = []
    for i in range(1, 51):
        try:
            data.append(fetch_data_by_id(i))
        except ValueError:
            logging.error(f"Plant with id '{i}' was not found")

    save_to_json(data)


if __name__ == "__main__":
    extract_data()
