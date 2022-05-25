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
from config import BASE_URL, MAX_RETRIES, RETRY_COOLDOWN, SNAPSHOTS_DIR, TIMEOUT, USER_AGENT, SNAPSHOTS
from bs4 import BeautifulSoup

def save_file(url, text):
    filename = SNAPSHOTS_DIR + "/" + str(int(time())) + "-" + url.split("/")[-1]
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(text)

def assemble_url(*components):
    return BASE_URL + "/".join(components)

def get(url, retry_count = 0 ):
    headers = {
        "User-Agent": USER_AGENT
    }

    try:
        r = preqs.get(
            url,
            headers = headers,
            timeout = TIMEOUT
        )
        return r
    except RequestException:
        if retry_count == MAX_RETRIES:
            raise Exception
        sleep(RETRY_COOLDOWN)
        return get(url, retry_count = (retry_count+1))

def get_file(url):
    r = get(url)
    if SNAPSHOTS:
        save_file(url, r.text)
    return BeautifulSoup(r.text, "xml")

def get_electorate(electorate_id: int):
    id_str = f'{electorate_id:02d}'
    url = assemble_url(f'e{id_str}', f'e{id_str}.xml')
    return get_file(url)

def get_votingplace(electorate_id: int, physical_electorate_id: int, voting_place_id: int):
    e_id_str = f'{electorate_id:02d}'
    pe_id_str = f'{physical_electorate_id:02d}'
    vp_id_str = f'{voting_place_id:03d}'
    url = assemble_url(f'e{e_id_str}', "votingplaces", f'{e_id_str}-{pe_id_str}{vp_id_str}.xml')
    return get_file(url)

def get_staticfile(name: str):
    valid = ["election", "candidates", "parties", "electorates", "votingplaces", "statistics"]
    if name not in valid:
        raise ValueError(f"get_staticfile: name must be one of {valid}")
    url = assemble_url(f'{name}.xml')
    return get_file(url)

