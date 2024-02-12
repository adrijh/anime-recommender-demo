import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter, Retry
from requests.sessions import Session

from f_poller import config as cfg
from f_poller.namespace import PollingSpec
from f_poller.sink import S3Sink, Sink
from f_poller.utils import get_auth_headers, read_event


class MALPoller:
    def __init__(self, sink: Sink):
        self.sink = sink
        self.headers = get_auth_headers()
        self.session = self.__create_requests_session()

    def poll_anime_data(self, spec: PollingSpec):
        print("Start polling...")
        next_page_url = None
        continue_polling = True

        while (continue_polling):
            print(f"Polling {spec.year} {spec.season_name} page {spec.current_page + 1}")
            anime_data, next_page_url = self.poll_seasonal_anime_page(spec, next_page_url)

            print(f"Saving {spec.year} {spec.season_name} page {spec.current_page + 1}")
            self.sink.save(anime_data, spec)

            spec = spec.increment_current_page()
            time.sleep(cfg.API_REQUEST_SLEEP)

            if not next_page_url:
                continue_polling = False

    def poll_seasonal_anime_page(
        self,
        spec: PollingSpec,
        next_page_url: str | None = None,
    ) -> tuple[list, str | None]:

        if not next_page_url:
            next_page_url = self.__build_request_url(spec)

        response = self.session.get(url=next_page_url, headers=self.headers, timeout=5).json()
        next_page_url = response.get("paging", {}).get("next")
        anime_data = map(
            lambda x: x["node"],
            response["data"],
        )
        return (list(anime_data), next_page_url)

    def __build_request_url(self, spec: PollingSpec) -> str:
        fields = ",".join([
            "id", "title", "main_picture", "alternative_titles",
            "start_date", "end_date", "synopsis", "mean", "rank",
            "popularity", "num_list_users", "num_scoring_users",
        ])
        return (
            f"{cfg.API_ENDPOINT}/anime/season/{spec.year}/{spec.season_name}"
            f"?limit={spec.page_limit}"
            f"&fields={fields}"
        )

    def __create_requests_session(self) -> Session:
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session



def main(event: dict[str, Any]) -> None:
    specs = read_event(event)
    sink = S3Sink(bucket_name=cfg.BUCKET_NAME)
    poller = MALPoller(sink=sink)

    for spec in specs:
        poller.poll_anime_data(spec)




