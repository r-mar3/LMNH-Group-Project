import requests as req

BASE_URL = 'https://sigma-labs-bot.herokuapp.com/api/plants/'


def fetch_data_by_id(id: int) -> dict:
    response = req.get(f"{BASE_URL}{id}")

    body = response.json()
    status_code = response.status_code
    if status_code == 404:
        raise ValueError(f"Plant with id {id} not found.")

    return {"status_code": status_code, "body": body}


def


if __name__ == "__main__":
    pass
