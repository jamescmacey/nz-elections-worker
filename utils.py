"""
utils.py
Created:     2 June 2022
Author:      James Macey
Description: MongoDB utilities.
"""

from pymongo.mongo_client import MongoClient
from config import MONGO_DATABASE, USE_MONGODB

from parsers.candidates import Candidates
from parsers.parties import Parties
from parsers.election import Election
from parsers.electorates import Electorates
from parsers.votingplaces import VotingPlaces
from parsers.statistics import Statistics

try:
    from secrets import MONGO_CONNECTION
except Exception as e:
    if USE_MONGODB:
        raise e

def get_db_handle():
    if not USE_MONGODB:
        return None
    client = MongoClient(MONGO_CONNECTION)
    return client[MONGO_DATABASE]

def replace_many(collection, items: list):
    for i in items:
        collection.replace_one({"_id": i.get("_id")}, i, upsert=True)

def set_candidates(candidates: Candidates):
    db = get_db_handle()
    
    # Update candidates
    replace_many(db.candidates, candidates.as_dict())

    ids = [x.get("_id") for x in candidates.as_dict()]

    # Remove all others
    db.candidates.delete_many({"_id": {"$nin": ids}})

def set_parties(parties: Parties):
    db = get_db_handle()
    
    # Update parties
    replace_many(db.parties, parties.as_dict())

    ids = [x.get("_id") for x in parties.as_dict()]

    # Remove all others
    db.parties.delete_many({"_id": {"$nin": ids}})

def set_election(election: Election):
    db = get_db_handle()
    elec_dict = election.as_dict()
    elec_dict["_id"] = "election"
    db.election.replace_one({"_id": "election" }, elec_dict, upsert=True)

def set_electorates(electorates: Electorates):
    db = get_db_handle()
    
    # Update electorates
    replace_many(db.electorates, electorates.as_dict())

    ids = [x.get("_id") for x in electorates.as_dict()]

    # Remove all others
    db.electorates.delete_many({"_id": {"$nin": ids}})

def set_voting_places(voting_places: VotingPlaces):
    db = get_db_handle()

    # Update voting places
    replace_many(db.voting_places, voting_places.as_dict())

    ids = [x.get("_id") for x in voting_places.as_dict()]

    # Remove all others
    db.voting_places.delete_many({"_id": {"$nin": ids}})

def set_electorate_results(electorate_results):
    db = get_db_handle()
    
    electorate_results_dicts = [x.as_dict() for x in electorate_results]

    print(len(electorate_results[0].voting_place_results))
    # Update electorate results
    replace_many(db.electorate_results, electorate_results_dicts)

    ids = [x.get("_id") for x in electorate_results_dicts]

    # Remove all others
    db.electorate_results.delete_many({"_id": {"$nin": ids}})

def set_statistics(statistics: Statistics):
    db = get_db_handle()
    stats_dict = statistics.as_dict()
    stats_dict["_id"] = "statistics"
    db.statistics.replace_one({"_id": "statistics" }, stats_dict, upsert=True)