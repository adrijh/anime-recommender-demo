import json
from typing import Any

import boto3

from f_poller import config as cfg
from f_poller.namespace import PollingSpec

ssm = boto3.client("ssm")


def read_event(event: dict[str, Any]) -> list[PollingSpec]:
    years = event["year"]
    season_names = event["season"]

    if not isinstance(years, list):
        years = [years]

    if not isinstance(season_names, list):
        season_names = [season_names]

    return [
        PollingSpec(year=year, season_name=season_name)
        for year in years
        for season_name in season_names
    ]

def get_auth_headers() -> dict:
    secrets = get_api_secrets()
    access_token = secrets["access_token"]
    return {"Authorization": f"Bearer {access_token}"}

def get_api_secrets() -> dict[str, str]:
    param_value = ssm.get_parameter(
        Name=cfg.API_SECRETS_PARAM,
        WithDecryption=True,
    )["Parameter"]["Value"]

    return json.loads(param_value)

# def get_code_verifier() -> str:
#     token = secrets.token_urlsafe(100)
#     return token[:128]
#
# def get_tokens():
#     secrets = get_api_secrets()
#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded",
#     }
#     data = {
#         "client_id": secrets["client_id"],
#         "client_secret": secrets["client_secret"],
#         "code": secrets["code"],
#         "code_verifier": secrets["code_verifier"],
#         "grant_type": "authorization_code"
#     }
#     response = requests.post(cfg.TOKEN_ENDPOINT, data=data, headers=headers, timeout=5)
#     print(response.text)
#     print(response.json())
