"""
votingplaces.py
Created:     25 May 2022
Author:      James Macey
Description: Class and parser for VotingPlace.
"""

from bs4.element import Tag
from bs4 import BeautifulSoup

class VotingPlace:
    id: int = None
    physical_electorate_id: int = None
    address: str = None
    latitude: float = None
    longitude: float = None

    def __init__(self, soup: Tag):
        self.id = int(soup.attrs["vp_id"])
        self.physical_electorate_id = int(soup.attrs["vp_e_no"])
        self.address = soup.find("vp_address").text
        try:
            self.latitude = float(soup.find("vp_lat").text)
            self.longitude = float(soup.find("vp_lon").text)
        except ValueError:
            pass

    def as_dict(self) -> dict:
        return {
            "_id": self.id,
            "id": self.id,
            "physical_electorate_id": self.id,
            "address": self.address,
            "longitude": self.longitude,
            "latitude": self.latitude
        }


class VotingPlaces(list):
    def __init__(self, soup: BeautifulSoup):
        places = soup.find_all("votingplace")
        for vp in places:
            self.append(VotingPlace(vp))

    def as_dict(self) -> list:
        return [x.as_dict() for x in self]