from dataclasses import dataclass
from datetime import date


@dataclass
class SearchJourneys:
    """Action for searching available journeys."""

    from_: str
    to: str
    date: date
