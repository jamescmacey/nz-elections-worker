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


class Electorates(list):
    def __init__(self, soup: BeautifulSoup):
        electorates = soup.find_all("electorate")
        for e in electorates:
            self.append(Electorate(e))