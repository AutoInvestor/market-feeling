from dataclasses import dataclass


@dataclass
class Company:
    id: str
    ticker: str
    name: str
