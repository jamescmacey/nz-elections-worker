"""
electorate_result.py
Created:     25 May 2022
Author:      James Macey
Description: Class and parser for ElectorateResult.
"""

from datetime import datetime
from bs4 import BeautifulSoup

from parsers.voting_place_result import VotingPlaceResult
from .candidate_votes import CandidateVotes
from .soft_type_conversions import sint

class ElectorateResult:
    updated: datetime = None
    is_final: bool = None
    id: int = None
    candidate_votes: CandidateVotes = None
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

    def __init__(self, soup: BeautifulSoup):
        electorate = soup.find("electorate")
        self.id = int(electorate.attrs["e_no"])
        self.updated = datetime.strptime(electorate.attrs["updated"], "%Y-%m-%dT%H:%M:%S")
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
        
        self.candidate_votes = CandidateVotes(electorate.find("candidatevotes"))


