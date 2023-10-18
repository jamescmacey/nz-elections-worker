"""
voting_place_result.py
Created:     25 May 2022
Author:      James Macey
Description: Class and parser for VotingPlaceResult.
"""

from datetime import datetime
import zoneinfo
from config import EVENT_ID
import typing
from bs4 import BeautifulSoup
from bs4.element import Tag
from .soft_type_conversions import sint
from parsers.all import Result, ResultsSet, ResultsLevel, ResultsCategory, ResultsType, Statistics, ResultParsingMode

class VotingPlaceResult:
    updated: datetime = None
    parsed: datetime = None
    id: int = None
    physical_electorate_id: int = None
    electorate_id: int = None
    voting_place_id: int = None

    received: datetime = None
    total_issued_ballot_papers: int = None
    total_party_informals: int = None
    total_candidate_informals: int = None

    candidate_results: typing.List[Result] = []
    party_results: typing.List[Result] = []

    def __init__(self, soup: BeautifulSoup):
        votingplace = soup.find("votingplace")
        self.parsed = datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland"))
        self.updated = datetime.strptime(votingplace.attrs["updated"], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland"))
        self.id = int(votingplace.attrs["vp_id"])
        self.physical_electorate_id = int(votingplace.attrs["vp_e_no"])
        self.electorate_id = int(votingplace.attrs["e_no"])
        self.voting_place_id = int(votingplace.attrs["vp_no"])

        try:
            self.received = datetime.strptime(votingplace.find("time_received").text, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland"))
        except:
            pass

        self.total_issued_ballot_papers = sint(votingplace.find("total_issued_ballot_papers").text)
        self.total_party_informals = sint(votingplace.find("total_party_informals").text)
        self.total_candidate_informals = sint(votingplace.find("total_candidate_informals").text)
        
        self.party_results = ResultsSet.parse_results(soup=votingplace.find("partyvotes"), mode=ResultParsingMode.PARTY)
        self.candidate_results = ResultsSet.parse_results(soup=votingplace.find("candidatevotes"), mode=ResultParsingMode.CANDIDATE)
        

    def results_sets(self):
        return [ResultsSet(
            event_id=EVENT_ID,
            name=None,
            results_level=ResultsLevel.VOTING_PLACE,
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
            received=self.received,
            electorate_id=self.electorate_id,
            voting_place_id=self.id,
            voting_place_no=self.voting_place_id,
            voting_place_location_electorate_id=self.physical_electorate_id,
            statistics=Statistics(
                total_issued_ballot_papers=self.total_issued_ballot_papers
            ),
            is_final=None
        ),
        ResultsSet(
            event_id=EVENT_ID,
            name=None,
            results_level=ResultsLevel.VOTING_PLACE,
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
            received=self.received,
            electorate_id=self.electorate_id,
            voting_place_id=self.id,
            voting_place_no=self.voting_place_id,
            voting_place_location_electorate_id=self.physical_electorate_id,
            statistics=Statistics(
                total_issued_ballot_papers=self.total_issued_ballot_papers
            ),
            is_final=None
        )] 