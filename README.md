# Elections worker
This repository contains the code for a worker to fetch and store election results from the New Zealand Electoral Commission's XML feed(s). It is primarily intended for use on election night.

This tool is very much still a work in progress.

## Missing functionality / issues
* Party votes are not yet supported at all (this tool was developed in a rush, for the Tauranga by-election)
* `election.xml` is retrieved through the `get_staticfile` function; this is not accurate, as `election.xml` is not a static file (although, it is at DOCROOT with the other files)
* There's actually no way to get a list of voting places for a given electorate via XML only. The list of voting places provided at `votingplaces.xml` contains the global ID number of the voting place, and the ID number of the physical electorate it's based in. But it doesn't contain a list of the electorates it issues votes for, and even its results files are named based on its electorate-specific ID numbers (which are different from its global ID number). Getting a list of voting place results for a given electorate requires scraping the HTML index page for the /eNN/votingplaces/ directory; this is how it is implemented currently, but note that this is not a solution endorsed in the XML feed documentation and could break in the future.
* This tool doesn't actually do anything with the information yet. Current plan is to have it upload to MongoDB, then use that as a basis for an API for a web client to visualise results. 