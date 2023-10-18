"""
candidates.py
Created:     25 May 2022
Author:      James Macey
Description: Class and parser for Candidate.
"""

from bs4 import BeautifulSoup
from .all import ElectionCandidate
from config import EVENT_ID

class Candidates(list):
    def __init__(self, soup: BeautifulSoup=None, premade_candidates=[]):
        if len(premade_candidates) > 0:
            for premade in premade_candidates:
                self.append(premade)
            return
        
        if soup == None:
            raise Exception("No soup provided to Candidates parser.")

        candidates = soup.find_all("candidate")
        for c in candidates:
            self.append(
                ElectionCandidate(
                    event_id=EVENT_ID,
                    name=c.find("candidate_name").text,
                    candidate_id=int(c.attrs["c_no"]),
                    electorate_id=(int(c.find("electorate").text) if int(c.find("electorate").text) != 0 else None),
                    party_id=(int(c.find("party").text) if int(c.find("party").text) != 0 else None),
                    list_pos=(int(c.find("list_no").text) if int(c.find("list_no").text) != 0 else None),
                )
            )

    def as_dict(self) -> list:
        return [x.__dict__ for x in self]