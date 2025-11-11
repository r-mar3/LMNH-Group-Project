# pylint: disable=logging-fstring-interpolation
"""Script transform raw data and clean it"""
import json
import logging
import argparse
import os

INPUT_FILE = './raw_data/plant_data_raw.json'


def get_plants() -> None:
    """Gets plants from a file of dicts"""
    with open(INPUT_FILE, 'rb') as f:
        raw = f.read(100)
        plants = json.loads(INPUT_FILE)
        print(plants)


if __name__ == "__main__":
    get_plants()
