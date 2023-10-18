"""
all.py
Created:     September 2023
Author:      James Macey
Description: Dataclasses, rather than normal classes.
"""

from dataclasses import dataclass, asdict
from enum import Enum
import datetime
import zoneinfo, typing
from bs4.element import Tag
from bson import ObjectId

"""
from utils import get_db_handle, replace_many
"""

def dict_factory(data):
    def convert_value(obj):
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, (Result, ResultsTarget, VotingPlaceNumberingScheme)):
            return asdict(obj, dict_factory=dict_factory)
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%S%z")
        if isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        if isinstance(obj, ObjectId):
            return str(obj)
        return obj
    return dict((k, convert_value(v)) for k, v in data)

@dataclass
class ResultsTarget:
    proportion: int
    target_time: datetime.datetime

class ResultsLevel(Enum):
    VOTING_PLACE = "voting_place"
    ELECTORATE = "electorate"
    NATIONAL = "national"

class ElectorateStatus(Enum):
    CURRENT = "current"
    FORMER = "former"
    NEW = "new"
    RETIRING = "retiring"

class ResultsType(Enum):
    ACTUAL = "actual"
    POLL = "poll"
    CUSTOM = "custom"

class ResultsCategory(Enum):
    PARTY_VOTES = "party_votes"
    CANDIDATE_VOTES = "candidate_votes"

class ElectionType(Enum):
    GENERAL = "general"
    BY_ELECTION = "by_election"

class ElectorateType(Enum):
    GENERAL = "general"
    MAORI = "māori"

class ElectoralSystem(Enum):
    MMP = "mmp"
    FPP = "fpp"

class ResultParsingMode(Enum):
    CANDIDATE = "candidate"
    PARTY = "party"

@dataclass
class PollSeries:
    _id: str
    id: str
    name: str
    slug: str
    description: str

@dataclass 
class VotingPlaceNumberingScheme:
    long_description: str
    short_code: str
    min_inclusive: int
    max_inclusive: int


@dataclass
class Event:
    name: str
    id: str
    _id: str
    slug: str
    description: str
    event_type: ResultsType
    election_type: ElectionType
    date: datetime.date
    voting_period_start: datetime.date
    voting_period_end: datetime.date
    embargo_start: datetime.datetime
    embargo_end: datetime.datetime
    poll_series_id: str
    result_targets: typing.List[ResultsTarget] = None
    comparison_events: typing.List[str] = None
    refdata_built: bool = False
    vp_finder_url: str = None
    vp_numbering_scheme: typing.List[VotingPlaceNumberingScheme] = None
    coalition_order_left: typing.List[str] = None
    coalition_order_right: typing.List[str] = None
    card_url: str = None
    incumbents: list = None

@dataclass
class Result:
    count: int = None
    per_cent: float = None
    candidate_id: int = None
    party_id: int = None
    list_seats: int = None
    electorate_seats: int = None
    total_seats: int = None
    
@dataclass
class Statistics:
    # Not all of these statistics will be applicable at all result levels.
    total_voting_places_counted: int = 0
    percent_voting_places_counted: float = 0
    total_votes_cast: int = 0
    percent_votes_cast: float = 0
    total_electorates_final: int = 0
    percent_electorates_final: float = 0
    total_minimal_votes: int = None # what is a minimal vote? not used by EC 2020
    total_special_votes: int = None # not used by EC 2020
    total_registered_parties: int = 0
    total_voting_places: int = None
    total_party_informals: int = None
    total_candidate_informals: int = None
    total_candidates: int = None
    total_issued_ballot_papers: int = None

@dataclass
class ResultsSet:
    event_id: int
    name: str
    results_level: ResultsLevel
    results_type: ResultsType
    results_category: ResultsCategory
    results: typing.List[Result]
    informals: int
    unknowns: int
    refused: int
    sample_size: int
    updated: datetime.datetime
    parsed: datetime.datetime
    updated_timestamp: float
    parsed_timestamp: float
    electorate_id: int
    voting_place_id: int
    voting_place_no: int
    statistics: Statistics
    is_final: bool = None
    received: datetime.datetime = None
    voting_place_location_electorate_id: int = None

    @staticmethod
    def parse_results(soup: Tag, mode: ResultParsingMode) -> typing.List[Result]:
        results = []
        if mode == ResultParsingMode.CANDIDATE:
            votes = soup.find_all("candidate")
            for v in votes:
                results.append(Result(
                    candidate_id = int(v.attrs["c_no"]),
                    count = int(v.find("votes").text),
                ))
        elif mode == ResultParsingMode.PARTY:
            votes = soup.find_all("party")
            for v in votes:
                results.append(Result(
                    party_id = int(v.attrs["p_no"]),
                    count = int(v.find("votes").text),
                ))
        return results

@dataclass
class ElectionElectorate:
    event_id: int
    electorate_id: int = None
    name: str = None
    persistent_electorate_id: int = None


@dataclass
class ElectionParty:
    event_id: int
    party_id: int
    name: str
    short_name: str
    abbreviation: str
    registered: bool
    persistent_party_id: str = None

@dataclass
class PersistentElectorate:
    slug: str
    name: str
    region: str
    description: str
    type: ElectorateType
    status: ElectorateStatus
    valid_from: str
    valid_to: str

@dataclass
class PersistentParty:
    display_name: str
    short_name: str
    abbreviation: str
    wts_id: int

@dataclass
class PersistentCandidate:
    wts_id: int
    display_name: str

@dataclass
class ElectionCandidate:
    event_id: int
    name: str
    candidate_id: int
    electorate_id: int
    party_id: int
    list_pos: int
    persistent_candidate_id: str = None
    is_dead: bool = False

@dataclass
class ElectionVotingPlace:
    event_id: int
    voting_place_id: int
    physical_electorate_id: int
    address: str
    latitude: float
    longitude: float
    persistent_voting_place_id: str = None

@dataclass
class PersistentVotingPlace:
    latitude: float
    longitude: float
    address: str


"""
polls = []
polls.append(
    PollSeries(
        id="1news",
        _id="1news",
        name="1News Verian",
        slug="1news",
        description="Formerly Kantar Public and Colmar Brunton.",
    )
)
polls.append(
    PollSeries(
        _id="newshub", id="newshub", name="Newshub Reid Research", slug="newshub", description=None
    )
)
polls.append(PollSeries(_id="curia", id="curia", name="Curia", slug="curia", description=None))
polls.append(
    PollSeries(_id="roy_morgan", id="roy_morgan", name="Roy Morgan", slug="roy-morgan", description=None)
)
polls.append(
    PollSeries(
        id="talbot_mills",
        _id="talbot_mills",
        name="Talbot Mills Research",
        slug="talbot-mills",
        description=None,
    )
)

ge23 = Event(
    name="2023 General Election",
    id="ge_2023",
    _id="ge_2023",
    slug="2023-general-election",
    description=None,
    event_type=ResultsType.ACTUAL,
    election_type=ElectionType.GENERAL,
    date=datetime.date(2023, 10, 14),
    voting_period_start=datetime.date(2023, 10, 2),
    voting_period_end=datetime.date(2023, 10, 14),
    embargo_start=datetime.datetime(
        2023, 10, 14, 0, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland")
    ),
    embargo_end=datetime.datetime(
        2023, 10, 14, 19, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland")
    ),
    poll_series_id=None,
)
ge20 = Event(
    name="2020 General Election",
    id="ge_2020",
    _id="ge_2020",
    slug="2020-general-election",
    description=None,
    event_type=ResultsType.ACTUAL,
    election_type=ElectionType.GENERAL,
    date=datetime.date(2020, 10, 17),
    voting_period_start=datetime.date(2020, 10, 3),
    voting_period_end=datetime.date(2020, 10, 17),
    embargo_start=datetime.datetime(
        2020, 10, 17, 0, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland")
    ),
    embargo_end=datetime.datetime(
        2020, 10, 17, 19, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland")
    ),
    poll_series_id=None,
)
ge17 = Event(
    name="2017 General Election",
    id="ge_2017",
    _id="ge_2017",
    slug="2017-general-election",
    description=None,
    event_type=ResultsType.ACTUAL,
    election_type=ElectionType.GENERAL,
    date=datetime.date(2017, 9, 23),
    voting_period_start=datetime.date(2017, 9, 11),
    voting_period_end=datetime.date(2017, 9, 23),
    embargo_start=datetime.datetime(
        2017, 9, 23, 0, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland")
    ),
    embargo_end=datetime.datetime(
        2017, 9, 23, 19, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland")
    ),
    poll_series_id=None,
)
by22b = Event(
    name="2022 Hamilton West By-election",
    id="by_2022_hamilton_west",
    _id="by_2022_hamilton_west",
    slug="2022-hamilton-west-by-election",
    description=None,
    event_type=ResultsType.ACTUAL,
    election_type=ElectionType.BY_ELECTION,
    date=datetime.date(2022, 12, 10),
    voting_period_start=datetime.date(2022, 11, 28),
    voting_period_end=datetime.date(2022, 12, 10),
    embargo_start=datetime.datetime(
        2022, 12, 10, 0, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland")
    ),
    embargo_end=datetime.datetime(
        2022, 12, 10, 19, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland")
    ),
    poll_series_id=None,
)
by22a = Event(
    name="2022 Tauranga By-election",
    id="by_2022_tauranga",
    _id="by_2022_tauranga",
    slug="2022-tauranga-by-election",
    description=None,
    event_type=ResultsType.ACTUAL,
    election_type=ElectionType.BY_ELECTION,
    date=datetime.date(2022, 6, 18),
    voting_period_start=datetime.date(2022, 6, 4),
    voting_period_end=datetime.date(2022, 6, 18),
    embargo_start=datetime.datetime(
        2022, 6, 18, 0, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland")
    ),
    embargo_end=datetime.datetime(
        2022, 6, 18, 19, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland")
    ),
    poll_series_id=None,
)

p_1_23_7 = Event(
    name="July 2023 1News Verian Poll",
    id="polls_2023_07_17_1news",
    _id="polls_2023_07_17_1news",
    slug="2023-07-17-1news",
    description=None,
    event_type=ResultsType.POLL,
    election_type=ElectionType.GENERAL,
    date=datetime.date(2023, 7, 17),
    voting_period_start=datetime.date(2023, 7, 8),
    voting_period_end=datetime.date(2023, 7, 12),
    embargo_start=None,
    embargo_end=None,
    poll_series_id="1news",
)

events = [ge23, ge20, ge17, by22a, by22b, p_1_23_7]

db = get_db_handle()
#replace_many(db.events, events)
#replace_many(db.poll_series, polls)

from requests import get
from orjson import loads

parties = loads(get("https://wheretheystand.nz/api/parties/", params={"group":"allLive"}).content)
for party in parties:
    nparty = PersistentParty(
        _id=str(party.get("id")),
        id=str(party.get("id")),
        wts_id=party.get("id"),
        slug=party.get("slug"),
        display_name=party.get("display_name"),
        legal_name=party.get("legal_name"),
        short_name=party.get("short_name"),
        hansard_name=party.get("hansard_name"),
        code=party.get("code"),
        colour=party.get("colour"),
        party_leader_role=party.get("party_leader_role"),
        party_leader_role_plural=party.get("party_leader_role_plural"),
    )
    replace_many(db.persistent_parties, [nparty], id_key="wts_id")



db = get_db_handle()
#replace_many(db.events, events)
#replace_many(db.poll_series, polls)

from requests import get
from orjson import loads, dumps


electorates = loads(get("https://wheretheystand.nz/api/electorates/", params={"group":"allCurrent"}).content) + loads(get("https://wheretheystand.nz/api/electorates/", params={"group":"allHistoric"}).content)
for electorate in electorates:
    full_electorate = loads(get("https://wheretheystand.nz/api/electorates/" + electorate.get("slug") + "/").content)

    nelectorate = PersistentElectorate(
        id=full_electorate.get("id"),
        _id=full_electorate.get("id"),
        slug=full_electorate.get("slug"),
        name=full_electorate.get("name"),
        region=full_electorate.get("region"),
        description=full_electorate.get("description"),
        type=ElectorateType(full_electorate.get("type")),
        status=ElectorateStatus(full_electorate.get("status")),
        valid_from=full_electorate.get("valid_from"),
        valid_to=full_electorate.get("valid_to"),
    )
    replace_many(db.persistent_electorates, [nelectorate.__dict__])

"""