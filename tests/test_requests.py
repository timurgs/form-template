import json

import requests

BASE_URL = "http://web:8000"


def test_post_request():
    url = f"{BASE_URL}/get_form"

    with open("tests/test_data.json", 'r') as f:
        test_data = json.load(f)

    for td in test_data:
        response = requests.post(url, data=td)
        if response.status_code == 200:
            print("POST request successful!")
            print("Response:", response.json())
        else:
            print("Failed to make POST request")
            print("Status code:", response.status_code)
            print("Response:", response.text)

if __name__ == "__main__":
    test_post_request()
