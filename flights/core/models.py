from dataclasses import dataclass, field
from datetime import datetime


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


@dataclass
class Journey:
    """Collection of one or more flight events to travel from A to B, with possible connections."""

    flight_events: list[FlightEvent] = field(default_factory=list)

    @property
    def connections(self) -> int:
        if not self.flight_events:
            return 0
        return len(self.flight_events) - 1
