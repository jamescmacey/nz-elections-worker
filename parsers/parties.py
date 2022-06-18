"""
parties.py
Created:     25 May 2022
Author:      James Macey
Description: Class and parser for Party.
"""

from bs4.element import Tag
from bs4 import BeautifulSoup

class Party:
    id: int = None
    name: str = None
    short_name: str = None
    abbreviation: str = None
    registered: bool = None

    def __init__(self, soup: Tag):
        self.id = int(soup.attrs["p_no"])
        self.name = soup.find("party_name").text
        self.short_name = soup.find("short_name").text
        self.abbreviation = soup.find("abbrev").text
        registered = soup.find("registered").text
        if registered == "yes":
            self.registered = True
        elif registered == "no":
            self.registered = False

    def as_dict(self) -> dict:
        return {
            "_id": self.id,
            "id": self.id,
            "name": self.name,
            "short_name": self.short_name,
            "abbreviation": self.abbreviation,
            "registered": self.registered
        }


class Parties(list):
    def __init__(self, soup: BeautifulSoup):
        parties = soup.find_all("party")
        for p in parties:
            self.append(Party(p))

    def as_dict(self) -> list:
        return [x.as_dict() for x in self]