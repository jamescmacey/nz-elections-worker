"""
worker.py
Created:     25 May 2022
Author:      James Macey
Description: Entry point. Runnable.
"""

from config import SLEEP_PERIOD
from interface import get_electorate, get_staticfile, get_votingplace
from parsers.candidates import Candidates
from parsers.election import Election
from parsers.electorates import Electorates
from parsers.statistics import Statistics
from parsers.parties import Parties
from parsers.votingplaces import VotingPlaces
from parsers.electorate_result import ElectorateResult
from time import sleep

def get_all_electorate_results(electorates: Electorates):
    electorate_results = []
    for electorate in electorates:
        electorate_results.append(ElectorateResult(get_electorate(electorate.id)))
    return electorate_results

def results_printout(candidates: Candidates, 
electorates: Electorates, 
parties: Parties,
electorate_results: list, electorate_id: int):
    # Get the given electorate and its results
    electorate = [x for x in electorates if x.id == electorate_id][0]
    results = [x for x in electorate_results if x.id == electorate_id][0]

    # Print out the electorate name header
    print("----------------")
    print(f"[{electorate_id}] {electorate.name}")
    print(f"Last updated: {results.updated}")
    print(f"Counted: {results.total_voting_places_counted}/{results.total_voting_places} ({results.percent_voting_places_counted}%)")
    print("----------------")
    results.candidate_votes.sort(key=lambda x: x.votes, reverse=True)
    for vote in results.candidate_votes:
        candidate = [x for x in candidates if x.id == vote.id][0]
        if candidate.party_id:
            party = [x for x in parties if x.id == candidate.party_id][0]
            party_code = party.abbreviation
        else:
            party_code = "---"
        print(f"[{party_code}] {vote.votes} votes: {candidate.name}")
    print("Candidate informals:", results.total_candidate_informals)
    print("----------------\n")


# Populate staticfiles
# This only happens once.
candidates = Candidates(get_staticfile("candidates"))
electorates = Electorates(get_staticfile("electorates"))
statistics = Statistics(get_staticfile("statistics"))
parties = Parties(get_staticfile("parties"))
voting_places = VotingPlaces(get_staticfile("votingplaces"))

### 
###
### [ upload static files to intermediary database / website backend]
###
###

# Populate the election file
election = Election(get_staticfile("election"))
electorate_results = get_all_electorate_results(electorates)
results_printout(candidates, electorates, parties, electorate_results, 52)

# Start the infinite loop.
while True:
    sleep(SLEEP_PERIOD)
    new_election = Election(get_staticfile("election"))
    if new_election.updated != election.updated:
        election = new_election
        electorate_results = get_all_electorate_results(electorates)

        ### 
        ###
        ### [ upload results to intermediary database / website backend]
        ###
        ###
        
        results_printout(candidates, electorates, parties, electorate_results, 52)

