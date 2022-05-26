"""
candidates.py
Created:     25 May 2022
Author:      James Macey
Description: Class and parser for Candidate.
"""

from datetime import datetime
from bs4.element import Tag
from bs4 import BeautifulSoup

class Candidate:
    name: str = None
    id: int = None
    electorate_id: int = None
    party_id: int = None
    list_pos: int = None
    def __init__(self, soup: Tag):
        self.name = soup.find("candidate_name").text
        self.id = int(soup.attrs["c_no"])
        self.electorate_id = int(soup.find("electorate").text)
        self.party_id = int(soup.find("party").text)
        self.list_pos = int(soup.find("list_no").text)

        if self.electorate_id == 0:
            self.electorate_id = None
        if self.party_id == 0:
            self.party_id = None
        if self.list_pos == 0:
            self.list_pos = None


class Candidates(list):
    def __init__(self, soup: BeautifulSoup):
        candidates = soup.find_all("candidate")
        for c in candidates:
            self.append(Candidate(c))