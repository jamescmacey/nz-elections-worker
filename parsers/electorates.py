"""
electorates.py
Created:     25 May 2022
Author:      James Macey
Description: Class and parser for Electorate.
"""

from bs4.element import Tag
from bs4 import BeautifulSoup

class Electorate:
    id: int = None
    name: str = None

    def __init__(self, soup: Tag):
        self.id = int(soup.attrs["e_no"])
        self.name = soup.find("electorate_name").text

    def as_dict(self) -> dict:
        return {
            "_id": self.id,
            "id": self.id,
            "name": self.name
        }


class Electorates(list):
    def __init__(self, soup: BeautifulSoup):
        electorates = soup.find_all("electorate")
        for e in electorates:
            self.append(Electorate(e))
    
    def as_dict(self) -> list:
        return [x.as_dict() for x in self]