from parsers.all import ElectionCandidate, ElectionElectorate, ElectionParty
import pandas as pd
import numpy as np
from interface import get_staticfile
from parsers.votingplaces import VotingPlaces
from parsers.candidates import Candidates
from parsers.electorates import Electorates
from parsers.parties import Parties
from parsers.statistics import Statistics as StatisticsParser
from parsers.election import Election
from parsers.electorate_result import ElectorateResult
from parsers.voting_place_result import VotingPlaceResult
from parsers.all import ResultsSet, ResultsLevel, ResultsCategory, ResultsType, Result, Statistics
from datetime import datetime
import zoneinfo

def build_synthetic_data(event_id):
    df = pd.read_csv("synthetics/2023_full_merged_candidates.csv")
    unique_parties = df[df["party"].notna()]["party"].unique()
    np.random.seed(234333)
    np.random.shuffle(unique_parties)
    party_id_count = 1

    party_name_lookup = {}
    election_parties = []
    for party in unique_parties:
        election_parties.append(
            ElectionParty(
                event_id=event_id,
                party_id=party_id_count,
                name=str(party),
                short_name=str(party),
                abbreviation=str(party)[:3],
                registered=True
            )
        )
        party_name_lookup[party] = party_id_count
        party_id_count += 1

    df["party"] = df["party"].map(party_name_lookup)

    electorate_lookup = {'Auckland Central': 1, 'Bay of Plenty': 3, 'Botany': 4, 'Christchurch Central': 5, 'Christchurch East': 6, 'Southland': 46, 'Coromandel': 7, 'Dunedin': 8, 'Taieri': 47, 'East Coast': 9, 'East Coast Bays': 10, 'Epsom': 11, 'Hamilton East': 12, 'Hamilton West': 13, 'Kaipara ki Mahurangi': 18, 'Port Waikato': 39, 'Hutt South': 14, 'Ilam': 15, 'Invercargill': 16, 'Kaikōura': 17, 'Kelston': 19, 'Hauraki-Waikato': 66, 'Ikaroa-Rāwhiti': 67, 'Tāmaki Makaurau': 68, 'Te Tai Hauāuru': 69, 'Te Tai Tokerau': 70, 'Te Tai Tonga': 71, 'Waiariki': 72, 'Mana': 20, 'Māngere': 21, 'Panmure-Ōtāhuhu': 37, 'Manurewa': 22, 'Maungakiekie': 23, 'Mt Albert': 24, 'Mt Roskill': 25, 'Napier': 26, 'Nelson': 27, 'New Lynn': 28, 'New Plymouth': 29, 'North Shore': 30, 'Northcote': 31, 'Northland': 32, 'Ōhāriu': 33, 'Ōtaki': 34, 'Pakuranga': 35, 'Palmerston North': 36, 'Papakura': 38, 'Banks Peninsula': 2, 'Rangitata': 40, 'Rangitīkei': 41, 'Remutaka': 42, 'Whangaparāoa': 63, 'Rongotai': 43, 'Rotorua': 44, 'Selwyn': 45, 'Tāmaki': 49, 'Taranaki-King Country': 50, 'Taupō': 51, 'Tauranga': 52, 'Te Atatū': 53, 'Tukituki': 54, 'Upper Harbour': 55, 'Waikato': 56, 'Waimakariri': 57, 'Wairarapa': 58, 'Waitaki': 59, 'Wellington Central': 60, 'West Coast-Tasman': 61, 'Whanganui': 62, 'Whangārei': 64, 'Wigram': 65, 'Takanini': 48}
    df["electorate"] = df["electorate"].map(electorate_lookup)

    election_electorates = []
    for electorate in electorate_lookup.keys():
        election_electorates.append(
            ElectionElectorate(
                event_id=event_id,
                electorate_id=electorate_lookup[electorate],
                name=electorate
            )
        )

    election_candidates = []
    for index, row in df.iterrows():
        election_candidates.append(
            ElectionCandidate(
                event_id=event_id,
                candidate_id=int(row["id"]),
                electorate_id=(int(row["electorate"]) if not np.isnan(row["electorate"]) else None),
                party_id=(int(row["party"]) if not np.isnan(row["party"]) else None),
                name=row["name"],
                list_pos=(int(row["list_pos"]) if not np.isnan(row["list_pos"]) else None),
            )
        )

    print(df.head())

    election_voting_places = VotingPlaces(get_staticfile("votingplaces", validators={}), event_id=event_id)
    statistics = StatisticsParser(get_staticfile("statistics", validators={}), event_id=event_id)

    return (Parties(premade_parties=election_parties), Electorates(premade_electorates=election_electorates), Candidates(premade_candidates=election_candidates), election_voting_places, statistics)

def generate_random_party_results(parties, seed=0):
    np.random.seed(seed)
    party_vote_counts = {
        "National Party": int(np.random.uniform(35,38,None)*10000),
        "Labour Party": int(np.random.uniform(25,29,None)*10000),
        "ACT New Zealand": int(np.random.uniform(11,13,None)*10000),
        "Green Party": int(np.random.uniform(11,13,None)*10000),
        "Te Pāti Māori": int(np.random.uniform(3,5,None)*10000),
        "New Zealand First Party": int(np.random.uniform(4,6,None)*10000)
    }

    results = []
    for party in parties:
        if party.name in ["ACT New Zealand", "Animal Justice Party", "Aotearoa Legalise Cannabis Party", "DemocracyNZ", "Freedoms NZ", "Green Party", "Labour Party", "Leighton Baker Party", "National Party", "New Conservatives", "New Nation Party", "NewZeal", "New Zealand First Party", "New Zealand Loyal", "Te Pāti Māori", "The Opportunities Party (TOP)", "Women's Rights Party"]:
            if party.name in party_vote_counts.keys():
                vote_count = party_vote_counts[party.name]
            else:
                vote_count = int(np.random.uniform(0.2,0.5,None)*10000)
                party_vote_counts[party.name] = vote_count
            results.append(Result(
                count=vote_count,
                per_cent=None,
                party_id=party.party_id,
                list_seats=0,
                electorate_seats=0,
                total_seats=0
            )
            )
    return results

def generate_random_electorate_results(electorate_id, candidates, parties, seed=0):
    np.random.seed(seed*233)
    party_vote_counts = {
        "National Party": int(np.random.uniform(25,38,None)*500),
        "Labour Party": int(np.random.uniform(25,38,None)*500),
        "ACT New Zealand": int(np.random.uniform(11,13,None)*500),
        "Green Party": int(np.random.uniform(11,13,None)*500),
        "Te Pāti Māori": int(np.random.uniform(3,5,None)*500),
        "New Zealand First Party": int(np.random.uniform(4,6,None)*500)
    }

    party_name_lookups = {}
    for party in parties:
        party_name_lookups[party.party_id] = party.name

    candidates = [x for x in candidates if x.electorate_id == electorate_id]

    results = []
    for candidate in candidates:
        if candidate.party_id is not None:
            party_name = party_name_lookups[candidate.party_id]
            if party_name in party_vote_counts.keys():
                vote_count = party_vote_counts[party_name]
            else:
                vote_count = int(np.random.uniform(1,5,None)*500)
                party_vote_counts[party_name] = vote_count
            results.append(Result(
                count=vote_count,
                candidate_id=candidate.candidate_id
            )
            )
        else:
            vote_count = int(np.random.uniform(1,5,None)*500)
            results.append(Result(
                count=vote_count,
                candidate_id=candidate.candidate_id
            )
            )
    return results

def generate_synthetic_electorates(parties,electorates,candidates,voting_places):
    electorate_results = []
    for electorate in electorates:
        candidate_results = generate_random_electorate_results(electorate.electorate_id, candidates, parties, seed=electorate.electorate_id)
        party_results = generate_random_party_results(parties, seed=electorate.electorate_id)
        party_informals = int(np.random.uniform(1,35,None))
        candidate_informals = int(np.random.uniform(1,35,None))
        results = [ResultsSet(
            event_id=electorate.event_id,
            name=None,
            results_level=ResultsLevel.ELECTORATE,
            results_type=ResultsType.ACTUAL,
            results_category=ResultsCategory.PARTY_VOTES,
            results=party_results,
            informals=party_informals,
            unknowns=None,
            refused=None,
            sample_size=party_informals + sum([x.count for x in party_results]),
            updated=datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland")),
            parsed=datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland")),
            updated_timestamp=datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland")).timestamp(),
            parsed_timestamp=datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland")).timestamp(),
            electorate_id=electorate.electorate_id,
            voting_place_id=None,
            voting_place_no=None,
            statistics=Statistics(
                total_voting_places=84,
                total_voting_places_counted=23,
                percent_voting_places_counted=45.34,
                total_registered_parties=19,
                percent_votes_cast=53.52,
                total_votes_cast=party_informals + sum([x.count for x in party_results])
            ),
            is_final=False
        ),
        ResultsSet(
            event_id=electorate.event_id,
            name=None,
            results_level=ResultsLevel.ELECTORATE,
            results_type=ResultsType.ACTUAL,
            results_category=ResultsCategory.CANDIDATE_VOTES,
            results=candidate_results,
            informals=candidate_informals,
            unknowns=None,
            refused=None,
            sample_size=candidate_informals + sum([x.count for x in candidate_results]),
            updated=datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland")),
            parsed=datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland")),
            updated_timestamp=datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland")).timestamp(),
            parsed_timestamp=datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland")).timestamp(),
            electorate_id=electorate.electorate_id,
            voting_place_id=None,
            voting_place_no=None,
            statistics=Statistics(
                total_voting_places=84,
                total_voting_places_counted=23,
                percent_voting_places_counted=45.34,
                total_registered_parties=19,
                percent_votes_cast=53.52,
                total_votes_cast=candidate_informals + sum([x.count for x in candidate_results])
            ),
            is_final=False
        )]
        electorate_results.append(ElectorateResult(soup=None,premade_results_sets=results))
    return electorate_results


def generate_synthetic_election(parties,electorates,candidates,voting_places):
    results = generate_random_party_results(parties)
    
    election = Election(soup=None, premade_results_set=ResultsSet(
        event_id=electorates[0].event_id,
        name=None,
        results_level=ResultsLevel.NATIONAL,
        results_type=ResultsType.ACTUAL,
        results_category=ResultsCategory.PARTY_VOTES,
        results=results,
        informals=None,
        unknowns=None,  
        refused=None,
        sample_size=None,
        updated=datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland")),
        parsed=datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland")),
        updated_timestamp=datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland")).timestamp(),
        parsed_timestamp=datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland")).timestamp(),
        electorate_id=None,
        voting_place_id=None,
        voting_place_no=None,
        statistics=Statistics(
            total_voting_places_counted=536,
            percent_voting_places_counted=34.53,
            total_votes_cast=235342,
            percent_votes_cast=23.44,
            total_electorates_final=0,
            percent_electorates_final=0.0,
            total_minimal_votes=None,
            total_special_votes=None,
            total_registered_parties=19,
        ),
        is_final=False
    ))

    return election

#parties, electorates, candidates, voting_places, statistics = build_synthetic_data("ge2023")
#election = generate_synthetic_election(parties, electorates, candidates, voting_places)
#electorate_results = generate_synthetic_electorates(parties, electorates, candidates, voting_places)
#from pprint import pprint
#pprint([x.results_sets() for x in electorate_results])