import os
from dotenv import load_dotenv

LOCAL_FOLDER = os.path.dirname(__file__)

load_dotenv(f"{LOCAL_FOLDER}/.env")

def main(event: dict) -> None:
    from f_poller.__main__ import MALPoller
    from f_poller.sink import FileSystemSink
    from f_poller.utils import read_event
    from f_poller import config as cfg

    specs = read_event(event)
    sink = FileSystemSink(data_folder=cfg.LOCAL_DATA_FOLDER)
    poller = MALPoller(sink=sink)

    for spec in specs:
        poller.poll_anime_data(spec)


if __name__ == "__main__":
    event = {
        "year": [2024],
        "season": ["winter"]
    }

    main(event)
