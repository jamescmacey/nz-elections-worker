"""
voting_place_result.py
Created:     25 May 2022
Author:      James Macey
Description: Class and parser for VotingPlaceResult.
"""

from datetime import datetime
from bs4 import BeautifulSoup
from bs4.element import Tag
from .candidate_votes import CandidateVotes
from .soft_type_conversions import sint

class VotingPlaceResult:
    updated: datetime = None
    received: datetime = None
    id: int = None
    physical_electorate_id: int = None
    electorate_id: int = None
    voting_place_id: int = None

    candidate_votes: CandidateVotes = None

    total_issued_ballot_papers: int = None
    total_party_informals: int = None
    total_candidate_informals: int = None

    def __init__(self, soup: BeautifulSoup):
        votingplace = soup.find("votingplace")
        self.updated = datetime.strptime(votingplace.attrs["updated"], "%Y-%m-%dT%H:%M:%S")
        self.id = int(votingplace.attrs["vp_id"])
        self.physical_electorate_id = int(votingplace.attrs["vp_e_no"])
        self.electorate_id = int(votingplace.attrs["e_no"])
        self.voting_place_id = int(votingplace.attrs["vp_no"])

        self.total_issued_ballot_papers = sint(votingplace.find("total_issued_ballot_papers").text)
        self.total_party_informals = sint(votingplace.find("total_party_informals").text)
        self.total_candidate_informals = sint(votingplace.find("total_candidate_informals").text)
        
        self.candidate_votes = CandidateVotes(votingplace.find("candidatevotes"))


