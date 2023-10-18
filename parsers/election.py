"""
election.py
Created:     25 May 2022
Author:      James Macey
Description: Class and parser for Election.
"""

from datetime import datetime
import zoneinfo
from bs4 import BeautifulSoup
from config import EVENT_ID
import typing
from .all import ResultsSet, ResultsLevel, ResultsCategory, ResultsType, Result, Statistics

class Election:
    updated: datetime = None
    parsed: datetime = None
    total_voting_places_counted: int = 0
    percent_voting_places_counted: float = 0
    total_votes_cast: int = 0
    percent_votes_cast: float = 0
    total_electorates_final: int = 0
    percent_electorates_final: float = 0
    total_minimal_votes: int = 0 # what is a minimal vote?
    total_special_votes: int = 0
    total_registered_parties: int = 0
    results: typing.List[Result] = []

    premade_results_set: ResultsSet = None

    def __init__(self, soup: BeautifulSoup, premade_results_set: ResultsSet = None):
        if premade_results_set is not None:
            self.premade_results_set = premade_results_set
            return
        election = soup.find("election")
        self.parsed = datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland"))
        self.updated = datetime.strptime(election.attrs["updated"], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland"))
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

        for result in election.find("partystatus").find_all("party"):
            self.results.append(
                Result(
                    count = int(result.find("votes").text),
                    per_cent = float(result.find("percent_votes").text),
                    party_id=result.attrs["p_no"],
                    list_seats=int(result.find("party_seats").text),
                    electorate_seats=int(result.find("candidate_seats").text),
                    total_seats=int(result.find("total_seats").text),
                )
            )

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

    def results_set(self) -> ResultsSet:
        if self.premade_results_set is not None:
            return self.premade_results_set

        return ResultsSet(
            event_id=EVENT_ID,
            name=None,
            results_level=ResultsLevel.NATIONAL,
            results_type=ResultsType.ACTUAL,
            results_category=ResultsCategory.PARTY_VOTES,
            results=self.results,
            informals=None,
            unknowns=None,
            refused=None,
            sample_size=None,
            updated=self.updated,
            parsed=self.parsed,
            updated_timestamp=self.updated.timestamp(),
            parsed_timestamp=self.parsed.timestamp(),
            electorate_id=None,
            voting_place_id=None,
            voting_place_no=None,
            statistics=Statistics(
                total_voting_places_counted=self.total_voting_places_counted,
                percent_voting_places_counted=self.percent_voting_places_counted,
                total_votes_cast=self.total_votes_cast,
                percent_votes_cast=self.percent_votes_cast,
                total_electorates_final=self.total_electorates_final,
                percent_electorates_final=self.percent_electorates_final,
                total_minimal_votes=self.total_minimal_votes,
                total_special_votes=self.total_special_votes,
                total_registered_parties=self.total_registered_parties,
            ),
            is_final=(True if self.percent_electorates_final == 100.0 else False)
        ) 