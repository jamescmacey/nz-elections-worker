"""
electorate_result.py
Created:     25 May 2022
Author:      James Macey
Description: Class and parser for ElectorateResult.
"""

from datetime import datetime
import zoneinfo
from bs4 import BeautifulSoup
from config import EVENT_ID
import typing
from parsers.all import Result, ResultsSet, ResultsLevel, ResultsCategory, ResultsType, Statistics, ResultParsingMode

from .soft_type_conversions import sint

class ElectorateResult:
    updated: datetime = None
    parsed: datetime = None
    is_final: bool = None
    id: int = None
    voting_place_results = []

    total_voting_places: int = None
    total_voting_places_counted: int = None
    percent_voting_places_counted: float = None
    total_votes_cast: int = None
    percent_votes_cast: float = None
    total_party_informals: int = None
    total_candidate_informals: int = None
    total_registered_parties: int = None
    total_candidates: int = None

    candidate_results: typing.List[Result] = []
    party_results: typing.List[Result] = []

    premade_results_sets: typing.List[ResultsSet] = None

    def __init__(self, soup: BeautifulSoup, premade_results_sets = None):
        if premade_results_sets is not None:
            self.premade_results_sets = premade_results_sets
            return
        electorate = soup.find("electorate")
        self.id = int(electorate.attrs["e_no"])
        self.parsed = datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland"))
        self.updated = datetime.strptime(electorate.attrs["updated"], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland"))
        is_final = electorate.attrs["final"]
        if is_final == "true":
            self.is_final = True
        elif is_final == "false":
            self.is_final = False

        self.total_voting_places = sint(electorate.find("total_voting_places").text)
        self.total_voting_places_counted = sint(electorate.find("total_voting_places_counted").text)
        self.percent_voting_places_counted = float(electorate.find("percent_voting_places_counted").text)
        self.total_votes_cast = sint(electorate.find("total_votes_cast").text)
        self.percent_votes_cast = float(electorate.find("percent_votes_cast").text)
        self.total_party_informals = sint(electorate.find("total_party_informals").text)
        self.total_candidate_informals = sint(electorate.find("total_candidate_informals").text)
        self.total_registered_parties = sint(electorate.find("total_registered_parties").text)
        self.total_candidates = sint(electorate.find("total_candidates").text)

        self.party_results = ResultsSet.parse_results(soup=electorate.find("partyvotes"), mode=ResultParsingMode.PARTY)
        self.candidate_results = ResultsSet.parse_results(soup=electorate.find("candidatevotes"), mode=ResultParsingMode.CANDIDATE)
        

    def results_sets(self):
        if self.premade_results_sets is not None:
            return self.premade_results_sets

        return [ResultsSet(
            event_id=EVENT_ID,
            name=None,
            results_level=ResultsLevel.ELECTORATE,
            results_type=ResultsType.ACTUAL,
            results_category=ResultsCategory.PARTY_VOTES,
            results=self.party_results,
            informals=self.total_party_informals,
            unknowns=None,
            refused=None,
            sample_size=self.total_party_informals + sum([x.count for x in self.party_results]),
            updated=self.updated,
            parsed=self.parsed,
            updated_timestamp=self.updated.timestamp(),
            parsed_timestamp=self.parsed.timestamp(),
            electorate_id=self.id,
            voting_place_id=None,
            voting_place_no=None,
            statistics=Statistics(
                total_voting_places=self.total_voting_places,
                total_voting_places_counted=self.total_voting_places_counted,
                percent_voting_places_counted=self.percent_voting_places_counted,
                total_registered_parties=self.total_registered_parties,
                percent_votes_cast=self.percent_votes_cast,
                total_votes_cast=self.total_votes_cast,
            ),
            is_final=self.is_final
        ),
        ResultsSet(
            event_id=EVENT_ID,
            name=None,
            results_level=ResultsLevel.ELECTORATE,
            results_type=ResultsType.ACTUAL,
            results_category=ResultsCategory.CANDIDATE_VOTES,
            results=self.candidate_results,
            informals=self.total_candidate_informals,
            unknowns=None,
            refused=None,
            sample_size=self.total_candidate_informals + sum([x.count for x in self.candidate_results]),
            updated=self.updated,
            parsed=self.parsed,
            updated_timestamp=self.updated.timestamp(),
            parsed_timestamp=self.parsed.timestamp(),
            electorate_id=self.id,
            voting_place_id=None,
            voting_place_no=None,
            statistics=Statistics(
                total_voting_places=self.total_voting_places,
                total_voting_places_counted=self.total_voting_places_counted,
                percent_voting_places_counted=self.percent_voting_places_counted,
                total_votes_cast=self.total_votes_cast,
                percent_votes_cast=self.percent_votes_cast,
                total_candidates=self.total_candidates,
            ),
            is_final=self.is_final
        )] 