"""
electorates.py
Created:     25 May 2022
Author:      James Macey
Description: Class and parser for Electorate.
"""

from bs4 import BeautifulSoup
from config import EVENT_ID
from .all import ElectionElectorate

class Electorates(list):
    def __init__(self, soup: BeautifulSoup=None, premade_electorates=[]):
        if len(premade_electorates) > 0:
            for premade in premade_electorates:
                self.append(premade)
            return
        
        if soup == None:
            raise Exception("No soup provided to Electorates parser.")

        electorates = soup.find_all("electorate")
        for e in electorates:
            self.append(ElectionElectorate(
                event_id=EVENT_ID,
                electorate_id=int(e.attrs["e_no"]),
                name=e.find("electorate_name").text
            ))
    
    def as_dict(self) -> list:
        return [x.__dict__ for x in self]