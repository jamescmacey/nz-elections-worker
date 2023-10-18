"""
worker.py
Created:     25 May 2022
Author:      James Macey
Description: Entry point. Runnable.
"""

from config import (
    SLEEP_PERIOD,
    USE_MONGODB,
    RECURSION,
    PULL_VOTING_PLACES,
    START_TIME,
    EXIT_TIME,
    VALIDATION,
    EVENT_ID,
    ELECTORATE_RANGE,
    SEND_HEARTBEATS,
    WORKER_ID,
    USE_PERSISTENCE,
    USE_SYNTHETIC_REFERENCE,
    USE_SYNTHETIC_RESULTS,
    RESULTS_MODE
)
from interface import (
    get_electorate,
    get_electorate_voting_places,
    get_staticfile,
    get_votingplace,
)
from parsers.candidates import Candidates
from parsers.election import Election
from parsers.electorates import Electorates
from parsers.statistics import Statistics
from parsers.parties import Parties
from parsers.votingplaces import VotingPlaces
from parsers.electorate_result import ElectorateResult
from parsers.electorate_voting_places import ElectorateVotingPlaces
from parsers.voting_place_result import VotingPlaceResult
from time import sleep
from exceptions import FileMissing
import datetime, zoneinfo
from heartbeats import Heartbeat
from synthetics import synthetics

from utils import set_candidates, set_voting_places, set_electorates, set_parties, set_statistics, set_election, set_electorate_results


# Update electorate results
def update_electorates(electorates, electorate_results):
    updated_results = []

    for electorate in electorates:
        if ELECTORATE_RANGE:
            if electorate.electorate_id not in ELECTORATE_RANGE:
                continue

        existing_result = [
            x for x in electorate_results if x.id == electorate.electorate_id
        ]

        # If we don't already have a result for this electorate — it will be updated.
        # If we do — check the new result, see if it is newer. If it is, update it too.
        if len(existing_result) == 0:
            print("NEW Electorate", electorate.electorate_id)
            try:
                updated_results.append(
                    ElectorateResult(
                        get_electorate(electorate.electorate_id, validators=VALIDATORS)
                    )
                )
            except FileMissing:
                print("??? Electorate", electorate.electorate_id)
                continue
        else:
            try:
                new_result = ElectorateResult(
                    get_electorate(electorate.electorate_id, validators=VALIDATORS)
                )
            except FileMissing:
                print("??? Electorate", electorate.electorate_id)
                continue
            existing_result = existing_result[0]
            if existing_result.updated == new_result.updated:
                print("NCG Electorate", electorate.electorate_id)
                continue
            elif existing_result.updated > new_result.updated:
                print("WARNING: Electorate rollback.")
            else:
                print("UPD Electorate", electorate.electorate_id)
                updated_results.append(new_result)

    # Populate all the new voting place results for that electorate.
    if PULL_VOTING_PLACES:
        for result in updated_results:
            voting_places = ElectorateVotingPlaces(
                get_electorate_voting_places(result.id)
            )
            result.voting_place_results = []
            for voting_place in voting_places:
                result.voting_place_results.append(
                    VotingPlaceResult(
                        get_votingplace(
                            voting_place.electorate_id,
                            voting_place.physical_electorate_id,
                            voting_place.voting_place_id,
                            validators=VALIDATORS,
                        )
                    )
                )

    # Now, combine the new results with the existing results.
    changed_results = updated_results
    for result in electorate_results:
        if len([x for x in updated_results if x.id == result.id]) == 0:
            updated_results.append(result)

    return updated_results, changed_results

if USE_MONGODB and SEND_HEARTBEATS:
    Heartbeat(worker_id=WORKER_ID, event_id=EVENT_ID, status="Starting").send()


# Pre-checks
VALIDATORS = {}
if VALIDATION:
    print("Checking validation files.")
    from config import VALIDATION_MAPPINGS
    from os import path, makedirs

    dir = "schemes"
    if not path.isdir(dir):
        makedirs(dir)
    keys = VALIDATION_MAPPINGS.keys()
    from lxml.etree import DTD

    for value in keys:
        if not path.isfile(path.join(dir, VALIDATION_MAPPINGS[value])):
            raise Exception("Validation scheme missing: " + VALIDATION_MAPPINGS[value])
        VALIDATORS[value] = DTD(path.join(dir, VALIDATION_MAPPINGS[value]))

if USE_MONGODB:
    print("Checking MongoDB connection.")
    from utils import get_db_handle

    db = get_db_handle()
    from pymongo.errors import ConnectionFailure

    try:
        event = db.events.find_one({"_id": EVENT_ID})
        print(f"Found event under event_id {EVENT_ID}: {event.get('name')}")
    except ConnectionFailure:
        print("Server not available")

# Don't start until the start time.
if START_TIME:
    print("START_TIME provided; waiting.")
    while True:
        if datetime.datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland")) < START_TIME:
            sleep(SLEEP_PERIOD + 1)
            if USE_MONGODB and SEND_HEARTBEATS:
                Heartbeat(worker_id=WORKER_ID, event_id=EVENT_ID, status="Waiting for START_TIME.").send()
        else:
            print("START_TIME passed; starting now.")
            if USE_MONGODB and SEND_HEARTBEATS:
                Heartbeat(worker_id=WORKER_ID, event_id=EVENT_ID, status="Proceeding as START_TIME has passed.").send()
            break
else:
    print("No START_TIME provided; starting immediately.")


# Populate staticfiles
# This only happens once.
if USE_SYNTHETIC_REFERENCE:
    parties, electorates, candidates, voting_places, statistics = synthetics.build_synthetic_data(EVENT_ID)
else:
    candidates = Candidates(get_staticfile("candidates", validators=VALIDATORS))
    electorates = Electorates(get_staticfile("electorates", validators=VALIDATORS))
    voting_places = VotingPlaces(get_staticfile("votingplaces", validators=VALIDATORS))
    parties = Parties(get_staticfile("parties", validators=VALIDATORS))
    statistics = Statistics(get_staticfile("statistics", validators=VALIDATORS))

if RESULTS_MODE:
    if USE_SYNTHETIC_RESULTS:
        election = synthetics.generate_synthetic_election(parties, electorates, candidates, voting_places)
    else:
        election = Election(get_staticfile("election", validators=VALIDATORS))

if USE_PERSISTENCE:
    from persistence import match_parties, match_candidates, match_electorates
    electorates = match_electorates(electorates)
    parties = match_parties(parties, candidates)
    candidates = match_candidates(candidates, parties)

if RESULTS_MODE:
    electorate_results = []
    if USE_SYNTHETIC_RESULTS:
        electorate_results = synthetics.generate_synthetic_electorates(parties, electorates, candidates, voting_places)
        changed_electorate_results = electorate_results
    else:
        electorate_results, changed_electorate_results = update_electorates(electorates, electorate_results)


if USE_MONGODB:
    set_candidates(candidates)
    set_electorates(electorates)
    set_statistics(statistics)
    set_parties(parties)
    set_voting_places(voting_places)
    db.events.update_one({"_id": EVENT_ID}, {"$set": {"refdata_built": True}})
    if RESULTS_MODE:
        set_election(election)
        set_electorate_results(electorate_results)


# Start the infinite loop.
while RECURSION and RESULTS_MODE:
    if USE_MONGODB and SEND_HEARTBEATS:
        Heartbeat(worker_id=WORKER_ID, event_id=EVENT_ID, status="Recurring.").send()
    sleep(SLEEP_PERIOD)
    if USE_SYNTHETIC_RESULTS:
        new_election = synthetics.generate_synthetic_election(parties, electorates, candidates, voting_places)
    else:
        new_election = Election(get_staticfile("election", validators=VALIDATORS))
    if new_election.updated != election.updated:
        if new_election.updated > election.updated:
            print("UPD Election")
            election = new_election
            if USE_SYNTHETIC_RESULTS:
                electorate_results = synthetics.generate_synthetic_electorates(parties, electorates, candidates, voting_places)
                changed_electorate_results = electorate_results
            else:
                electorate_results, changed_electorate_results = update_electorates(electorates, electorate_results)

            if USE_MONGODB:
                set_election(election)
                set_electorate_results(changed_electorate_results)

        else:
            print("WARNING: Election rollback.")
    else:
        print("NCG Election")
        if EXIT_TIME:
            if datetime.datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland")) > EXIT_TIME:
                if USE_MONGODB and SEND_HEARTBEATS:
                    Heartbeat(worker_id=WORKER_ID, event_id=EVENT_ID, status="Exiting as EXIT_TIME has passed.").send()
                print("Past EXIT_TIME; ending.")
                break
