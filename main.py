import os
from pprint import pprint as pp
from time import sleep
import requests

from dotenv import load_dotenv

BASE_AUTH_URL = "https://auth.apps.paloaltonetworks.com/auth/v1/oauth2/access_token"
BASE_API_URL = "https://api.strata.paloaltonetworks.com"


HEADERS = {
    "Accept": "application/json",
}

UPLOAD_HEADERS = {"Content-Type": "plain/text", "Content-Encoding": "gzip"}

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
    payload = {"delete_after_processing": True}
    try:
        response = requests.request(
            method="POST", url=url, headers=HEADERS, json=payload
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error creating upload link: {e}")
        return None


def upload_config(upload_url, config_file):
    print(f"Uploading config file {config_file} to {upload_url}")
    with open(config_file, "rb") as f:
        try:
            response = requests.request(
                method="PUT", url=upload_url, headers=UPLOAD_HEADERS, data=f
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error uploading config: {e}")
            return None


def get_task_id(task_id):
    print(f"Getting task status for task id {task_id}")
    url = f"{BASE_API_URL}/posture/checks/v1/reports/{str(task_id)}/bpa-result"
    try:
        response = requests.request(method="GET", url=url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error getting task status: {e}")
        return None


if __name__ == "__main__":
    config_file = f"{CONFIG_FOLDER}candidate-config.xml"
    create_token()

    # Get link to upload config
    created_job = create_upload_link()
    print(created_job)
    upload_config(created_job["upload_url"], config_file)

    # Wait for config to be processed
    task_status = get_task_id(created_job["task_id"])
    print(task_status)
