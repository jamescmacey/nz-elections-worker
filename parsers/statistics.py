"""
statistics.py
Created:     25 May 2022
Author:      James Macey
Description: Class and parser for Statistics.
"""

from datetime import datetime
import zoneinfo
from bs4 import BeautifulSoup

from config import EVENT_ID

class Statistics:
    updated: datetime = None
    parsed: datetime = None
    total_registered_parties: int = None
    total_all_parties: int = None
    total_electorates: int = None
    total_candidates: int = None
    total_voting_places: int = None
    total_electors: int = None
    event_id: str = None

    def __init__(self, soup: BeautifulSoup, event_id=None):
        if not event_id:
            event_id = EVENT_ID
        statistics = soup.find("statistics")
        self.updated = datetime.strptime(statistics.attrs["updated"], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland"))
        self.parsed = datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland"))
        self.total_registered_parties = int(statistics.find("total_registered_parties").text)
        self.total_all_parties = int(statistics.find("total_all_parties").text)
        self.total_electorates = int(statistics.find("total_electorates").text)
        self.total_candidates = int(statistics.find("total_candidates").text)
        self.total_voting_places = int(statistics.find("total_voting_places").text)
        self.total_electors = int(statistics.find("total_electors").text)

    def as_dict(self) -> dict:
        return {
            "updated": self.updated,
            "parsed": self.parsed,
            "event_id": self.event_id,
            "total_registered_parties": self.total_registered_parties,
            "total_all_parties": self.total_all_parties,
            "total_electorates": self.total_electorates,
            "total_candidates": self.total_candidates,
            "total_voting_places": self.total_voting_places,
            "total_electors": self.total_electors,
        }