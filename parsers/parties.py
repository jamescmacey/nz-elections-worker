"""
parties.py
Created:     25 May 2022
Author:      James Macey
Description: Class and parser for Party.
"""

from bs4 import BeautifulSoup
from .all import ElectionParty
from config import EVENT_ID

class Parties(list):
    def __init__(self, soup: BeautifulSoup=None, premade_parties=[]):
        if len(premade_parties) > 0:
            for premade in premade_parties:
                self.append(premade)
            return
        
        if soup == None:
            raise Exception("No soup provided to Parties parser.")
        
        parties = soup.find_all("party")
        for p in parties:
            self.append(ElectionParty(
                event_id=EVENT_ID,
                party_id=int(p.attrs["p_no"]),
                name = p.find("party_name").text,
                short_name = p.find("short_name").text,
                abbreviation = p.find("abbrev").text,
                registered = (True if p.find("registered").text == "yes" else False)
            ))

    def as_dict(self) -> list:
        return [x.__dict__ for x in self]