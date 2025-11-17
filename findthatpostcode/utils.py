from dataclasses import dataclass


@dataclass
class Field:
    id: str
    name: str
    location: str | None = None
    has_name: bool = False
    area: str | None = None
