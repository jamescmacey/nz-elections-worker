"""
config.py
Created:     25 May 2022
Author:      James Macey
Description: General configuration for this tool.
"""


# ELECTION NIGHT
# --------------

# The ID of the Event under which Results Sets will be saved.
EVENT_ID = "ge2023_prelim"

# MongoDB Database
# The MongoDB database to use. 
# You should have your MongoDB connection string stored as MONGO_CONNECTION in secrets.py.
MONGO_DATABASE = "wts_elections"


# Worker ID. 
# You may be using multiple workers.
WORKER_ID = "wts-eci-1"

# Timings
# Either can be None to ignore (to start straight away, or keep going until terminated)
# If recursion is enabled, the script will exit if there are no more updates and the exit time has passed.
# If a start time is provided, the script will wait until the start time beore starting.
import datetime, zoneinfo
EXIT_TIME = datetime.datetime(2023, 10, 15, 6, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland"))
START_TIME = datetime.datetime(2023, 10, 14, 19, 0, 0, 0, tzinfo=zoneinfo.ZoneInfo("Pacific/Auckland"))
#START_TIME = None

# User-Agent to use in all requests to Electoral Commission servers.
USER_AGENT = f"Mozilla/5.0 (compatible; WhereTheyStandElectionsWorker/{WORKER_ID}/0.1; +https://github.com/jamescmacey/)"

# Base URL
# (see MFTD Chapter 6 for fall-back URLs)
# [must include the trailing slash]
BASE_URL = "https://media.election.net.nz/electionresults_2023_preliminary/xml/"

# Fallback URL gets used on the third retry.
# See media feed specifications for all fallback URLs.
FALLBACK_URL = "https://dr.electionresults.govt.nz/xml/"

# Recursion
# If disabled, the worker will only run once (useful to gather up all the files from a previous election).
# If enabled, the worker will run live scraping.
RECURSION = True

# Voting places
# For general elections, pulling data from the voting place level can take up a lot of time.
# I'd recommend having two workers running: one doing electorate and election level only data, the other doing voting place data.
# For by-elections, it's fine to just have the one worker that's doing voting places too.
PULL_VOTING_PLACES = True

# Electorate restrictions
# For faster updating you might want to assign different electorates to different workers.
# e.g ELECTORATE_RANGE = range(1,35) will only do electorates numbered 1 through 34.
# Set as None to do all electorates (or equivalent would be a range that includes all electorates)
ELECTORATE_RANGE = None

# Sleep period (seconds)
# (sleep period between checking election.xml file)
SLEEP_PERIOD = 10

# Validation
VALIDATION = False
VALIDATION_MAPPINGS = {
    "candidates": "refdata-candidates-1.1.dtd",
    "electorates": "refdata-electorates-1.1.dtd",
    "parties": "refdata-parties-1.1.dtd",
    "votingplaces": "refdata-votingplaces-1.1.dtd",
    "election": "results-election-1.1.dtd",
    "electorate": "results-electorate-1.1.dtd",
    "votingplace": "results-votingplace-1.1.dtd",
}

# "statistics": "refdata-statistics-1.1.dtd",
# Stats file was failing validation

# Snapshots
# (each time a file is downloaded, save it to the disk;
# this is useful for debugging)
SNAPSHOTS = True
SNAPSHOTS_DIR = EVENT_ID
if SNAPSHOTS:
    from os import path, makedirs
    dir = path.join("snaps",SNAPSHOTS_DIR)
    if not path.isdir(dir):
        makedirs(dir)

# Timeout period (seconds)
# (timeout for all requests to Electoral Commission servers)
TIMEOUT = 10

# Max retries
# (if a request error happens, how many times to retry)
MAX_RETRIES = 3

# Retry cooldown (seconds)
# (if a request error happens, how many seconds to wait)
RETRY_COOLDOWN = 5

# Use MongoDB
# Whether or not the worker should interface with MongoDB
USE_MONGODB = False

# Use persistence
# This almost always requires custom code written election-by-election. 
USE_PERSISTENCE = False 

# Get results
# If False, the worker will not get any results; just the reference data
RESULTS_MODE = True

# Synthetic data generation
USE_SYNTHETIC_REFERENCE = False
USE_SYNTHETIC_RESULTS = False

# Send Heartbeats
# Whether or not to send heartbeats to the database.
# Will be ignored if USE_MONGODB is False.
SEND_HEARTBEATS = True