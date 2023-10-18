"""
interface.py
Created:     25 May 2022
Author:      James Macey
Description: Proxy functions for all requests to EC servers.
"""

from time import sleep, time
import requests as preqs
from requests.exceptions import RequestException
import os
from config import BASE_URL, MAX_RETRIES, RETRY_COOLDOWN, SNAPSHOTS_DIR, TIMEOUT, USER_AGENT, SNAPSHOTS, FALLBACK_URL
from bs4 import BeautifulSoup
from exceptions import FileMissing, ValidationError
from lxml.etree import DTD, XML

class URL:
    url = None
    path = None

    def __init__(self, *components):
        self.path = "/".join(components)
        self.url = BASE_URL + "/".join(components)

    def __str__(self):
        return "URL: " + str(self.url)
    
    def __repr__(self):
        return "URL: " + str(self.url)

def save_file(url: URL, text: str, filetype: str):
    filename = "snaps/" + SNAPSHOTS_DIR + "/" + "/".join(url.path.split("/")[:-1]) + "/" + str(int(time())) + "-" + url.path.split("/")[-1]
    if not filename.endswith("." + filetype):
        filename = filename + "." + filetype
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(text)

def get(url: URL, retry_count: int = 0 ):
    headers = {
        "User-Agent": USER_AGENT
    }

    try:
        get_url = url.url
        if retry_count >= 2:
            get_url = get_url.replace(BASE_URL, FALLBACK_URL)
        print("GET", get_url)
        r = preqs.get(
            url.url,
            headers = headers,
            timeout = TIMEOUT
        )

        if r.status_code == 404:
            raise FileMissing
        
        return r
    except RequestException as e:
        print("     Exception",e)
        if retry_count == MAX_RETRIES:
            raise Exception
        sleep(RETRY_COOLDOWN)
        return get(url, retry_count = (retry_count+1))
    
def validate_xml(content: str, dtd: DTD) -> bool:
    root = XML(content)
    return dtd.validate(root)
    
def get_file(url: URL, parser: str = "xml", dtd: DTD = None) -> BeautifulSoup:
    valid = ["html", "xml"]
    if parser not in valid:
        raise ValueError(f"get_file: parser must be one of {valid}")
    r = get(url)
    if SNAPSHOTS:
        save_file(url, r.text, parser)

    if parser == "xml" and dtd:
        validation = validate_xml(r.content, dtd)
        if not validation:
            raise ValidationError(f"get_file: {url} failed validation.")

    bs_parser = {"xml":"lxml-xml","html":"html.parser"}[parser]
    return BeautifulSoup(r.text, bs_parser)

def load_file(filename: str, parser: str = "xml") -> BeautifulSoup:
    filename = SNAPSHOTS_DIR + "/" + filename
    valid = ["html", "xml"]
    if parser not in valid:
        raise ValueError(f"load_file: parser must be one of {valid}")
    bs_parser = {"xml":"lxml-xml","html":"html.parser"}[parser]
    with open(filename) as f:
        soup = BeautifulSoup(f, bs_parser)
    return soup

def get_electorate(electorate_id: int, validators: dict = {}):
    id_str = f'{electorate_id:02d}'
    url = URL(f'e{id_str}', f'e{id_str}.xml')
    dtd = validators.get("electorate", None)
    return get_file(url, dtd = dtd)

def get_electorate_voting_places(electorate_id: int):
    e_id_str = f'{electorate_id:02d}'
    url = URL(f'e{e_id_str}', "votingplaces/")
    url.path = url.path + "index.html"
    return get_file(url, parser = "html")

def get_votingplace(electorate_id: int, physical_electorate_id: int, voting_place_id: int, validators: dict = {}):
    e_id_str = f'{electorate_id:02d}'
    pe_id_str = f'{physical_electorate_id:02d}'
    vp_id_str = f'{voting_place_id:03d}'
    url = URL(f'e{e_id_str}', "votingplaces", f'{e_id_str}-{pe_id_str}{vp_id_str}.xml')
    dtd = validators.get("votingplace", None)
    return get_file(url, dtd = dtd)

def get_staticfile(name: str, validators: dict = {}):
    valid = ["election", "candidates", "parties", "electorates", "votingplaces", "statistics","root"]
    dtd = validators.get(name, None)
    if name not in valid:
        raise ValueError(f"get_staticfile: name must be one of {valid}")
    if name == "root":
        url = URL("")
    else:
        url = URL(f'{name}.xml')
    return get_file(url, dtd = dtd)