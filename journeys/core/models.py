from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta


@dataclass
class FlightEvent:
    """Specific instance for a flight that will happen at certain time and between two cities."""

    flight_number: str
    from_: str
    to: str
    departure_time: datetime
    arrival_time: datetime

    def mask_flight_number(self):
        self.flight_number = f'XX{self.flight_number[2:]}' if len(self.flight_number) > 2 else self.flight_number

    def matches_from_and_time(self, from_: str, date_: date) -> bool:
        """Return true if flight matches the filtered origin city, departure time and doesn't take more than 24 hours."""
        return (
            self.from_ == from_
            and self.departure_time.date() == date_
            and self.arrival_time - self.departure_time <= timedelta(hours=24)
        )


@dataclass
class Journey:
    """Collection of one or more flight events to travel from A to B, with possible connections."""

    flight_events: list[FlightEvent] = field(default_factory=list)

    @property
    def connections(self) -> int:
        if not self.flight_events:
            return 0
        return len(self.flight_events) - 1


class JourneyBuilder:
    """Responsible for creating Journey objects from flight events."""

    def build_direct(self, flight_event: FlightEvent) -> Journey:
        fe = deepcopy(flight_event)
        fe.mask_flight_number()
        return Journey(flight_events=[fe])

    def build_with_connection(self, first: FlightEvent, second: FlightEvent) -> Journey:
        first_copy = deepcopy(first)
        second_copy = deepcopy(second)
        first_copy.mask_flight_number()
        second_copy.mask_flight_number()
        return Journey(flight_events=[first_copy, second_copy])
