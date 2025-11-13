# pylint: disable=logging-fstring-interpolation
"""Script to extract data from the plants api and save to .json file"""
import json
import logging
import argparse
import os
import multiprocessing
import requests as req
import time

BASE_URL = 'http://sigma-labs-bot.herokuapp.com/api/plants/'
OUTPUT_FOLDER = '.tmp/data/raw_data/'
OUTPUT_FILE = f'{OUTPUT_FOLDER}plant_data_raw.json'
BASE_NUM_ENDPOINTS = 50  # The number of endpoints to fetch from by default
NUM_PROCESSES_FETCH = 32  # The number of processes to use for reading the api
NUM_PROCESSES_CHECK = 4  # The number of processes to use for checking new endpoints
REQUEST_TIMEOUT = 5  # Time in seconds for each request timeout


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
    response = req.get(f"{BASE_URL}{plant_id}", timeout=REQUEST_TIMEOUT)

    status_code = response.status_code
    body = response.json()

    return {'status_code': status_code, 'body': body}


def save_to_json(data: list[dict]) -> None:
    """Saves list of dicts with plant data to a single json file"""
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def check_new_endpoints() -> int:
    """Checks for new endpoints and returns max endpoint to be read"""
    current_max_endpoint = BASE_NUM_ENDPOINTS

    new_endpoints = True

    while new_endpoints:
        with multiprocessing.Pool(NUM_PROCESSES_CHECK) as pool:
            data = pool.map(fetch_data_by_id, range(
                current_max_endpoint, current_max_endpoint + 5))

        for endpoint in data:
            if endpoint.get('status_code') == 200:
                current_max_endpoint += 5
                break

            new_endpoints = False

    return current_max_endpoint


def extract_data() -> None:
    """Runs the extract functions for all ids and catches error"""
    data = []
    max_endpoint = check_new_endpoints()
    with multiprocessing.Pool(NUM_PROCESSES_FETCH) as pool:
        data = pool.map(fetch_data_by_id, range(1, max_endpoint + 1))

    successful_data = [
        response.get('body') for response in data if response.get('status_code') == 200]

    save_to_json(successful_data)


if __name__ == "__main__":
    start_time = time.time()
    set_up_logging()
    extract_data()
    end_time = time.time()
    time_taken = end_time - start_time
    logging.info('Time taken = %s', time_taken)
