"""
config.py
Created:     25 May 2022
Author:      James Macey
Description: General configuration for this tool.
"""

# User-Agent to use in all requests to Electoral Commission servers.
USER_AGENT = "Mozilla/5.0 (compatible; WhereTheyStandElectionsWorker/0.1; +https://github.com/jamescmacey/)"

# Base URL
# (see MFTD Chapter 6 for fall-back URLs)
# [must include the trailing slash]
BASE_URL = "https://media.election.net.nz/xml/"

# Sleep period (seconds)
# (sleep period between checking election.xml file)
SLEEP_PERIOD = 30

# Snapshots
# (each time a file is downloaded, save it to the disk;
# this is useful for debugging)
SNAPSHOTS = True
SNAPSHOTS_DIR = "byelection"
if SNAPSHOTS:
    from os import path, makedirs
    if not path.isdir(SNAPSHOTS_DIR):
        makedirs(SNAPSHOTS_DIR)

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
USE_MONGODB = True

# MongoDB Database
# The MongoDB database to use. 
# You should have your MongoDB connection string stored as MONGO_CONNECTION in secrets.py.
MONGO_DATABASE = "2022-tga-by-prod"