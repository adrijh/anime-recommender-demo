from dataclasses import dataclass


@dataclass(frozen=True)
class AnimeRecord:
    anime_id: str
    title: str | None
    title_en: str | None
    main_picture: str | None
    start_date: str | None
    end_date: str | None
    synopsis: str | None
    mean: float
    rank: int
    popularity: int
    num_list_users: int
    num_scoring_users: int
