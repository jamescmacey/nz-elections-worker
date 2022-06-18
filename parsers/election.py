"""
election.py
Created:     25 May 2022
Author:      James Macey
Description: Class and parser for Election.
"""

from datetime import datetime
from bs4 import BeautifulSoup

class Election:
    updated: datetime = None
    total_voting_places_counted: int = 0
    percent_voting_places_counted: float = 0
    total_votes_cast: int = 0
    percent_votes_cast: float = 0
    total_electorates_final: int = 0
    percent_electorates_final: float = 0
    total_minimal_votes: int = 0 # what is a minimal vote?
    total_special_votes: int = 0
    total_registered_parties: int = 0

    def __init__(self, soup: BeautifulSoup):
        election = soup.find("election")
        self.updated = datetime.strptime(election.attrs["updated"], "%Y-%m-%dT%H:%M:%S")
        statistics = election.find("statistics")
        self.total_voting_places_counted = int(statistics.find("total_voting_places_counted").text)
        self.percent_voting_places_counted = float(statistics.find("percent_voting_places_counted").text)
        self.total_votes_cast = int(statistics.find("total_votes_cast").text)
        self.percent_votes_cast = float(statistics.find("percent_votes_cast").text)
        self.total_electorates_final = int(statistics.find("total_electorates_final").text)
        self.percent_electorates_final = float(statistics.find("percent_electorates_final").text)
        self.total_minimal_votes = int(statistics.find("total_minimal_votes").text)
        self.total_special_votes = int(statistics.find("total_special_votes").text)
        self.total_registered_parties = int(statistics.find("total_registered_parties").text)

    def as_dict(self) -> dict:
        return {
            "updated": self.updated,
            "total_voting_places_counted": self.total_voting_places_counted,
            "percent_voting_places_counted": self.percent_voting_places_counted,
            "total_votes_cast": self.total_votes_cast,
            "percent_votes_cast": self.percent_votes_cast,
            "total_electorates_final": self.total_electorates_final,
            "percent_electorates_final": self.percent_electorates_final,
            "total_minimal_votes": self.total_minimal_votes,
            "total_special_votes": self.total_special_votes,
            "total_registered_parties": self.total_registered_parties,
        }