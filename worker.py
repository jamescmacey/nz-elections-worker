"""
worker.py
Created:     25 May 2022
Author:      James Macey
Description: Entry point. Runnable.
"""

from config import SLEEP_PERIOD
from interface import get_electorate, get_electorate_voting_places, get_staticfile, get_votingplace
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
    print("----------------")
    for voting_place_result in results.voting_place_results:
        address = [x for x in voting_places if x.id == voting_place_result.id][0].address
        print(f"{address[0:30]}: {voting_place_result.total_issued_ballot_papers}")
    print("----------------\n")


# Update electorate results
def update_electorates(electorates):
    electorate_results = get_all_electorate_results(electorates)
    for result in electorate_results:
        voting_places = ElectorateVotingPlaces(get_electorate_voting_places(result.id))
        for voting_place in voting_places:
            result.voting_place_results.append(VotingPlaceResult(get_votingplace(voting_place.electorate_id, voting_place.physical_electorate_id, voting_place.voting_place_id)))
    return electorate_results


# Populate staticfiles
# This only happens once.
candidates = Candidates(get_staticfile("candidates"))
electorates = Electorates(get_staticfile("electorates"))
statistics = Statistics(get_staticfile("statistics"))
parties = Parties(get_staticfile("parties"))
voting_places = VotingPlaces(get_staticfile("votingplaces"))

election = Election(get_staticfile("election"))
electorate_results = update_electorates(electorates)
results_printout(candidates, electorates, parties, electorate_results, 52)

### 
###
### [ upload to intermediary database / website backend ]
###
###


# Start the infinite loop.
while True:
    sleep(SLEEP_PERIOD)
    new_election = Election(get_staticfile("election"))
    if new_election.updated != election.updated:
        election = new_election
        electorate_results = update_electorates(electorates)

        ### 
        ###
        ### [ upload results to intermediary database / website backend ]
        ###
        ###
        
        results_printout(candidates, electorates, parties, electorate_results, 52)

