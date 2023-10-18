"""
utils.py
Created:     2 June 2022
Author:      James Macey
Description: MongoDB utilities.
"""

from pymongo.mongo_client import MongoClient
from pymongo import ReplaceOne, InsertOne, UpdateOne
from config import MONGO_DATABASE, USE_MONGODB, PULL_VOTING_PLACES

from parsers.candidates import Candidates
from parsers.parties import Parties
from parsers.election import Election
from parsers.electorates import Electorates
from parsers.votingplaces import VotingPlaces
from parsers.statistics import Statistics
from config import EVENT_ID
from itertools import chain
from dataclasses import asdict

from parsers.all import dict_factory
from orjson import dumps, loads


try:
    from secret import MONGO_CONNECTION
except Exception as e:
    if USE_MONGODB:
        raise e

def get_db_handle():
    if not USE_MONGODB:
        return None
    client = MongoClient(MONGO_CONNECTION)
    return client[MONGO_DATABASE]

def replace_many(collection, items: list, id_key="_id", id_keys: list = None, event_scope=None, guard_field=None):
    if not id_keys:
        id_keys = [id_key]

    operations = []
    for i in items:
        d = loads(dumps(i))
        filter = {}

        for key in id_keys:
            filter[key] = d.get(key)

        if event_scope:
            filter["event_id"] = event_scope

        # If the guard_field is being used, we only want to update entries where there is a newer value.
        # However, we can't leave upsert on. The reason for this is that if the version we have is older,
        # we don't want it inserted as a new entry. But, we still want any new entries to be inserted.
        #
        # So, do a round of replacing, but don't upsert if the version we have is too old.
        # Then, do a round of updating. Update everything, but use set on insert to only
        # actually modify any fields if there is an upsert going on.
        if guard_field:
            guarded_filter = dict(filter)
            guarded_filter[guard_field] = {"$lt": d.get(guard_field)}
            operations.append(ReplaceOne(guarded_filter, d, upsert=False))
            operations.append(UpdateOne(filter, {"$setOnInsert": d}, upsert=True))
        else:
            operations.append(ReplaceOne(filter, d, upsert=True))

    if len(operations) > 0:
        print(f"DB: Bulk replacing {len(items)} items")
        collection.bulk_write(operations)
    else:
        print("DB: No operations to execute.")


def set_candidates(candidates: Candidates):
    db = get_db_handle()
    
    # Update candidates
    replace_many(db.election_candidates, [asdict(x, dict_factory=dict_factory) for x in candidates], id_key="candidate_id", event_scope=EVENT_ID)

    ids = [x.get("candidate_id") for x in [asdict(x, dict_factory=dict_factory) for x in candidates]]

    # Remove all others
    db.election_candidates.delete_many({"candidate_id": {"$nin": ids}, "event_id": EVENT_ID})

def set_parties(parties: Parties):
    db = get_db_handle()
    
    # Update parties
    replace_many(db.election_parties, [asdict(x, dict_factory=dict_factory) for x in parties], id_key="party_id", event_scope=EVENT_ID)

    ids = [x.get("party_id") for x in [asdict(x, dict_factory=dict_factory) for x in parties]]

    # Remove all others
    db.election_parties.delete_many({"party_id": {"$nin": ids}, "event_id": EVENT_ID})


def set_election(election: Election):
    db = get_db_handle()
    elec_dict = asdict(election.results_set(), dict_factory=dict_factory)
    replace_many(db.results, [elec_dict], id_key="results_level", event_scope=EVENT_ID, guard_field="updated_timestamp")

def set_electorates(electorates: Electorates):
    db = get_db_handle()
    
    # Update electorates
    replace_many(db.election_electorates, [asdict(x, dict_factory=dict_factory) for x in electorates], id_key="electorate_id", event_scope=EVENT_ID)

    ids = [x.get("electorate_id") for x in [asdict(x, dict_factory=dict_factory) for x in electorates]]

    # Remove all others
    db.election_electorates.delete_many({"electorate_id": {"$nin": ids}, "event_id": EVENT_ID})

def set_voting_places(voting_places: VotingPlaces):
    db = get_db_handle()

    # Update voting places
    replace_many(db.election_voting_places, voting_places.as_dict(), id_key="voting_place_id", event_scope=EVENT_ID)

    ids = [x.get("voting_place_id") for x in voting_places.as_dict()]

    # Remove all others
    db.election_voting_places.delete_many({"voting_place_id": {"$nin": ids}, "event_id": EVENT_ID})

def set_electorate_results(electorate_results):
    db = get_db_handle()

    electorate_results_dicts = [[asdict(y, dict_factory=dict_factory) for y in x.results_sets()] for x in electorate_results]
    electorate_results_dicts = list(chain.from_iterable(electorate_results_dicts))

    # Update electorate results
    replace_many(db.results, electorate_results_dicts, id_keys=["electorate_id", "results_level", "results_category"], event_scope=EVENT_ID, guard_field="updated_timestamp")

    if PULL_VOTING_PLACES:
        all_voting_place_updates = []
        for electorate_result in electorate_results:
            voting_place_results = electorate_result.voting_place_results
            voting_place_results_dicts = [[asdict(y, dict_factory=dict_factory) for y in x.results_sets()] for x in voting_place_results]
            voting_place_results_dicts = list(chain.from_iterable(voting_place_results_dicts))
            all_voting_place_updates += voting_place_results_dicts
        # Update voting place results
        replace_many(db.results, all_voting_place_updates, id_keys=["results_level", "results_category", "electorate_id", "voting_place_id", "voting_place_no", "voting_place_location_electorate_id"], event_scope=EVENT_ID, guard_field="updated_timestamp")


def set_statistics(statistics: Statistics):
    db = get_db_handle()
    stats_dict = statistics.as_dict()
    stats_dict["_id"] = EVENT_ID
    db.statistics.replace_one({"_id": EVENT_ID }, stats_dict, upsert=True)