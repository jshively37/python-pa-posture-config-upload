import os
from time import sleep
import requests

from dotenv import load_dotenv

BASE_AUTH_URL = "https://auth.apps.paloaltonetworks.com/auth/v1/oauth2/access_token"
BASE_API_URL = "https://api.strata.paloaltonetworks.com"


HEADERS = {
    "Accept": "application/json",
}

UPLOAD_HEADERS = {
    "Content-Type": "plain/text",
    "Content-Encoding": "gzip"
}

AUTH_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
}

# Time to sleep between requests in seconds.
SLEEP_TIME = 15

# Config folder
CONFIG_FOLDER = "configs.local/"

load_dotenv()
TSG_ID = os.environ.get("TSG_ID")
CLIENT_ID = os.environ.get("CLIENT_ID")
SECRET_ID = os.environ.get("SECRET_ID")


def create_token():
    auth_url = f"{BASE_AUTH_URL}?grant_type=client_credentials&scope:tsg_id:{TSG_ID}"

    token = requests.request(
        method="POST",
        url=auth_url,
        headers=AUTH_HEADERS,
        auth=(CLIENT_ID, SECRET_ID),
    ).json()
    HEADERS.update({"Authorization": f'Bearer {token["access_token"]}'})


def create_upload_link():
    url = f"{BASE_API_URL}/posture/checks/v1/reports/config-file-upload"
    payload = {
        "delete_after_processing": True
    }
    try:
        response = requests.request(method="POST", url=url, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error creating upload link: {e}")
        return None


def upload_config(upload_url, config_file):
    with open(config_file, "rb") as f:
        response = requests.request(method="PUT", url=upload_url, headers=UPLOAD_HEADERS, data=f)
    print(response.raise_for_status())


if __name__ == "__main__":
    config_file = f"{CONFIG_FOLDER}candidate-config.xml"
    create_token()

    # Get link to upload config
    upload_url = create_upload_link()
    print(upload_url)
    # upload_config(upload_url, config_file)

    # Upload config

    # Wait for config to be processed

    # Return results
