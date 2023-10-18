##########
# This code is used to match election candidates, parties, electorates and voting places to their persistent equivalents.
# This allows the comparison of results between elections.
#
# Naturally, this is hard to do. ID numbers change.
# This code must therefore be rewritten before each election to ensure the match goes correctly.
#
#
#
##########

from parsers.all import ElectionElectorate, ElectionCandidate, ElectionParty, ElectionVotingPlace
import typing
from pymongo.cursor import Cursor
import pandas as pd
from geopy import distance
from utils import get_db_handle

def match_electorates(electorates: typing.List[ElectionElectorate]) -> typing.List[ElectionElectorate]:
    # In 2023, we know the electorate IDs WILL be the same as in 2020.
    lookup = {1: 2, 3: 3, 4: 4, 5: 5, 6: 6, 46: 82, 7: 8, 8: 80, 47: 81, 9: 11, 10: 12, 11: 13, 12: 14, 13: 15, 18: 73, 39: 77, 14: 18, 15: 19, 16: 20, 17: 21, 19: 22, 66: 65, 67: 66, 68: 67, 69: 68, 70: 69, 71: 70, 72: 71, 20: 23, 21: 24, 37: 75, 22: 26, 23: 27, 24: 28, 25: 29, 26: 30, 27: 31, 28: 32, 29: 33, 30: 34, 31: 35, 32: 36, 33: 37, 34: 38, 35: 39, 36: 40, 38: 41, 2: 79, 40: 43, 41: 44, 42: 78, 63: 74, 43: 47, 44: 48, 45: 49, 49: 50, 50: 51, 51: 52, 52: 1, 53: 53, 54: 54, 55: 55, 56: 56, 57: 57, 58: 58, 59: 59, 60: 60, 61: 61, 62: 62, 64: 72, 65: 64, 48: 76}
    new_electorates = []
    for electorate in electorates:
        electorate.persistent_electorate_id = lookup.get(electorate.electorate_id)
        new_electorates.append(electorate)
    return new_electorates

def match_candidates(candidates: typing.List[ElectionCandidate], parties: typing.List[ElectionParty]) -> typing.List[ElectionCandidate]:
    elec_matching = pd.read_csv("persistence_files/2023_electorate_only_matching.csv")
    list_matching = pd.read_csv("persistence_files/2023_list_matching.csv")
    list_matching_death_adjusted = pd.read_csv("persistence_files/2023_list_matching_death_adjusted.csv")

    electorate_lookup = {'Auckland Central': 1, 'Bay of Plenty': 3, 'Botany': 4, 'Christchurch Central': 5, 'Christchurch East': 6, 'Southland': 46, 'Coromandel': 7, 'Dunedin': 8, 'Taieri': 47, 'East Coast': 9, 'East Coast Bays': 10, 'Epsom': 11, 'Hamilton East': 12, 'Hamilton West': 13, 'Kaipara ki Mahurangi': 18, 'Port Waikato': 39, 'Hutt South': 14, 'Ilam': 15, 'Invercargill': 16, 'Kaikōura': 17, 'Kelston': 19, 'Hauraki-Waikato': 66, 'Ikaroa-Rāwhiti': 67, 'Tāmaki Makaurau': 68, 'Te Tai Hauāuru': 69, 'Te Tai Tokerau': 70, 'Te Tai Tonga': 71, 'Waiariki': 72, 'Mana': 20, 'Māngere': 21, 'Panmure-Ōtāhuhu': 37, 'Manurewa': 22, 'Maungakiekie': 23, 'Mt Albert': 24, 'Mt Roskill': 25, 'Napier': 26, 'Nelson': 27, 'New Lynn': 28, 'New Plymouth': 29, 'North Shore': 30, 'Northcote': 31, 'Northland': 32, 'Ōhāriu': 33, 'Ōtaki': 34, 'Pakuranga': 35, 'Palmerston North': 36, 'Papakura': 38, 'Banks Peninsula': 2, 'Rangitata': 40, 'Rangitīkei': 41, 'Remutaka': 42, 'Whangaparāoa': 63, 'Rongotai': 43, 'Rotorua': 44, 'Selwyn': 45, 'Tāmaki': 49, 'Taranaki-King Country': 50, 'Taupō': 51, 'Tauranga': 52, 'Te Atatū': 53, 'Tukituki': 54, 'Upper Harbour': 55, 'Waikato': 56, 'Waimakariri': 57, 'Wairarapa': 58, 'Waitaki': 59, 'Wellington Central': 60, 'West Coast-Tasman': 61, 'Whanganui': 62, 'Whangārei': 64, 'Wigram': 65, 'Takanini': 48}

    elec_matching["electorate_name"] = elec_matching["electorate_name"].map(electorate_lookup)
    elec_matching.rename({"electorate_name": "electorate_id"}, axis=1, inplace=True)

    party_lookup = {x.party_id: str(x.persistent_party_id) for x in parties}
    list_lookup_model = {}
    elec_lookup_model = {}

    # This snippet - along with the death-adjusted matching list - was added in after Neil Christensen's death.
    # I was not sure before election night if they would do this or leave the list numbers the same.
    # So I prepared for both cases.
    for candidate in candidates:
        if candidate.name.startswith("ANDERSON") and "DION" in candidate.name.upper():
                if candidate.list_pos == 36:
                    # Do nothing - the list numbers below 36 have not been adjusted by the Electoral Commission to account for Christensen's death.
                    pass
                elif candidate.list_pos == 35:
                    print("ANDERSON, Dion is pos 35 instead of 36: using death-adjusted lists")
                    list_matching = list_matching_death_adjusted

    for index, row in list_matching.iterrows():
        if row["party"] not in list_lookup_model.keys():
            list_lookup_model[row["party"]] = {}
        list_lookup_model[row["party"]][row["list_pos"]] = row["candidate"]
    
    for index, row in elec_matching.iterrows():
        if row["electorate_id"] not in elec_lookup_model.keys():
            elec_lookup_model[row["electorate_id"]] = {}
        elec_lookup_model[row["electorate_id"]][row["name"]] = row["persistent_candidate_id"]

    new_candidates = []

    
    for candidate in candidates:
        if candidate.name.startswith("CHRISTENSEN"):
            candidate.is_dead = True

        if candidate.list_pos == None or candidate.party_id == None:
            elec_candidate_persistent_id = elec_lookup_model.get(candidate.electorate_id, {}).get(candidate.name)
            if elec_candidate_persistent_id:
                candidate.persistent_candidate_id = elec_candidate_persistent_id
            new_candidates.append(candidate)
            continue
        candidate_party_persistent_id = party_lookup.get(candidate.party_id)
        if candidate_party_persistent_id == None:
            new_candidates.append(candidate)
            continue
        candidate_persistent_id = list_lookup_model.get(candidate_party_persistent_id, {}).get(candidate.list_pos)
        if candidate_persistent_id:
            candidate.persistent_candidate_id = candidate_persistent_id
        new_candidates.append(candidate)

    print("Matched", len([x for x in new_candidates if x.persistent_candidate_id != None]), "out of", len(new_candidates), "candidates.")
    return new_candidates

def match_parties(parties: typing.List[ElectionParty], candidates: typing.List[ElectionCandidate]) -> typing.List[ElectionParty]:
    first_ranked = [candidate for candidate in candidates if candidate.list_pos == 1]
    party_keys = {}
    name_keys = {
        "BAKER": "6522240a6d9b75f5428cc2aa",
        "DAVIDSON": "6521429a0327fbb14e67be39",
        "GUNN": "6522240a6d9b75f5428cc2ab",
        "HERBERT": "6521429d0327fbb14e67be53",
        "HIPKINS": "6521429a0327fbb14e67be3c",
        "HOUGHTON": "6521429c0327fbb14e67be51",
        "JACOMB": "6522240a6d9b75f5428cc2a8",
        "KING": "6522240a6d9b75f5428cc2a9",
        "LUXON": "6521429b0327fbb14e67be3f",
        "MANJI": "6521429b0327fbb14e67be47",
        "MCNEIL": "6522240a6d9b75f5428cc2a7",
        "NGAREWA": "6521429a0327fbb14e67be3d",
        "NGARO": "6521429d0327fbb14e67be54",
        "OVENS": "6522240a6d9b75f5428cc2b3",
        "PETERS": "6521429b0327fbb14e67be40",
        "SEYMOUR": "6521429a0327fbb14e67be34",
        "TAMAKI": "6522240a6d9b75f5428cc2b2"
    }

    for candidate in first_ranked:
        for key in name_keys.keys():
            if candidate.name.upper().startswith(key.upper()):
                party_keys[candidate.party_id] = name_keys[key]

    db = get_db_handle()
    matched_ids = list(party_keys.values())

    new_parties = []
    for party in parties:
        # Match on list ranking: this is a more reliable match
        if party.party_id in party_keys.keys():
            party.persistent_party_id = party_keys[party.party_id]
            new_parties.append(party)
            continue
        
        # Match on name
        found_one = db.persistent_parties.find_one({"_id": {"$nin": matched_ids}, "display_name": party.name})
        if found_one:
            party.persistent_party_id = found_one["_id"]
            matched_ids.append(found_one["_id"])
            new_parties.append(party)
            continue


        new_parties.append(party)
    
    return new_parties

def match_voting_places(voting_places: Cursor) -> typing.List[dict]:
    # This takes a while to run, so I'm 
    db = get_db_handle()
    df = pd.DataFrame.from_records(db.persistent_voting_places.find())

    new_voting_places = []
    voting_places = list(voting_places)

    for voting_place in voting_places:
        if not (voting_place.get("latitude") and voting_place.get("longitude")):
            new_voting_places.append(voting_place)
        else:
            cp_df = df.copy()
            distances =cp_df.apply(lambda row: distance.distance((row["latitude"], row["longitude"]), (voting_place["latitude"], voting_place["longitude"])).m, axis=1)
            cp_df["distance"] = distances
            cp_df.sort_values("distance", inplace=True)
            closest = cp_df.iloc[0]
            if closest["distance"] < 50:
                voting_place["persistent_voting_place_id"] = closest["_id"]
                print("Matched", voting_place["address"],"with", closest["address"], "at", closest["distance"], "m")
            new_voting_places.append(voting_place)
    return new_voting_places

"""
from synthetics.reference import build_synthetic_data

parties, electorates, candidates, voting_places, statistics = build_synthetic_data("matchingtest")
parties = match_parties(parties, candidates)
candidates = match_candidates(candidates, parties)

from dataclasses import asdict
from parsers.all import dict_factory
election_candidates = pd.DataFrame.from_records([asdict(x, dict_factory=dict_factory) for x in candidates])
election_parties = pd.DataFrame.from_records([asdict(x, dict_factory=dict_factory) for x in parties])

from utils import get_db_handle
db = get_db_handle()

persistent_parties = pd.DataFrame.from_records(db.persistent_parties.find())
persistent_candidates = pd.DataFrame.from_records(db.persistent_candidates.find())

persistent_parties.rename({"_id":"persistent_party_id"}, inplace=True, axis=1)
persistent_parties["persistent_party_id"] = persistent_parties["persistent_party_id"].astype(str)
election_parties["persistent_party_id"] = election_parties["persistent_party_id"].astype(str)

persistent_candidates.rename({"_id":"persistent_candidate_id"}, inplace=True, axis=1)
persistent_candidates["persistent_candidate_id"] = persistent_candidates["persistent_candidate_id"].astype(str)
election_candidates["persistent_candidate_id"] = election_candidates["persistent_candidate_id"].astype(str)

parties = election_parties.merge(persistent_parties, on="persistent_party_id", how="left", suffixes=("","_persistent"))
candidates = election_candidates.merge(persistent_candidates, on="persistent_candidate_id", how="left", suffixes=("","_persistent"))

merged_df = candidates.merge(parties, on="party_id", how="left", suffixes=("","_party"))

print(merged_df.head())

merged_df.to_csv("persistence_merge_test.csv", index=False)
"""