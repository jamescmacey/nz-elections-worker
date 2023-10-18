"""
votingplaces.py
Created:     25 May 2022
Author:      James Macey
Description: Class and parser for VotingPlace.
"""

from bs4.element import Tag
from bs4 import BeautifulSoup
from .all import ElectionVotingPlace
from config import EVENT_ID

class VotingPlaces(list):
    def __init__(self, soup: BeautifulSoup, event_id=None):
        places = soup.find_all("votingplace")
        if not event_id:
            event_id = EVENT_ID
        for vp in places:
            try:
                lat = float(vp.find("vp_lat").text)
                lon = float(vp.find("vp_lon").text)
            except (ValueError, AttributeError):
                lat = None
                lon = None

            self.append(ElectionVotingPlace(
                event_id=event_id,
                voting_place_id=int(vp.attrs["vp_id"]),
                physical_electorate_id=int(vp.attrs["vp_e_no"]),
                address=vp.find("vp_address").text,
                latitude=lat,
                longitude=lon
            ))

    def as_dict(self) -> list:
        return [x.__dict__ for x in self]