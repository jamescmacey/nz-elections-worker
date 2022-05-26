"""
electorate_voting_places.py
Created:     25 May 2022
Author:      James Macey
Description: Class and parser for ElectorateVotingPlace.
"""

from bs4.element import Tag
from bs4 import BeautifulSoup

class ElectorateVotingPlace:
    electorate_id: int = None
    physical_electorate_id: int = None
    voting_place_id: int = None

    def __init__(self, filename: str):
        self.electorate_id = int(filename[0:2])
        self.physical_electorate_id = int(filename[3:5])
        self.voting_place_id = int(filename[5:8])
        


class ElectorateVotingPlaces(list):
    def __init__(self, soup: BeautifulSoup):
        table_cells = soup.find_all("td")
        already_done = []
        for cell in table_cells:
            link = cell.find("a")
            if link and link.text.strip().endswith(".xml") and link.text.strip() not in already_done:
                already_done.append(link.text.strip())
                self.append(ElectorateVotingPlace(link.text.strip()))