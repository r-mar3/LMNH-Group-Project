import logging
from extract import extract_data
from transform import transform_data
from load import load_data


def run_pipeline():
    logging.basicConfig(level=logging.ERROR)
    extract_data()
    transform_data()
    load_data()


def lambda_handler(event, context):
    run_pipeline()


if __name__ == "__main__":
    lambda_handler({}, {})
