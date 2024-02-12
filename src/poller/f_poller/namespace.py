from dataclasses import dataclass


@dataclass
class PollingSpec:
    year: int
    season_name: str
    page_limit: int = 100
    current_page: int = 0

    def increment_current_page(self):
        return PollingSpec(
            year=self.year,
            season_name=self.season_name,
            page_limit=self.page_limit,
            current_page=self.current_page + 1,
        )
