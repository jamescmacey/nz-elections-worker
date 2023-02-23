# Elections worker
This repository contains the code for a worker to fetch and store election results from the New Zealand Electoral Commission's XML feed(s). It is primarily intended for use on election night.

This tool is very much still a work in progress: most notably, it does not have support for party votes, so cannot yet be used for general elections. However, it should still be adequate for by-elections.

## Missing functionality / issues
* Party votes are not yet supported at all (this tool was developed in a rush, for the Tauranga by-election)
* `election.xml` is retrieved through the `get_staticfile` function; this is not accurate, as `election.xml` is not a static file (although, it is at DOCROOT with the other files)
* There's actually no way to get a list of voting places for a given electorate via XML only. The list of voting places provided at `votingplaces.xml` contains the global ID number of the voting place, and the ID number of the physical electorate it's based in. But it doesn't contain a list of the electorates it issues votes for, and even its results files are named based on its electorate-specific ID numbers (which are different from its global ID number). Getting a list of voting place results for a given electorate requires scraping the HTML index page for the /eNN/votingplaces/ directory; this is how it is implemented currently, but note that this is not a solution endorsed in the XML feed documentation and could break in the future.
* There is no rollback prevention. During the 2022 Hamilton West by-election, the Electoral Commission's servers incorrectly served out of date results files momentarily on a few occasions during the night. This meant that the results rolled back to an earlier state; future versions of this tool will guard against this.

## Helpful information
* Voting place numbering can be confusing. Even if you obtain the techinical specifications for the feed from the Commission, this is not explained, so here's how that works:
  * The votingplace.xml file has a list of voting place *locations*, not voting places. 
  * Each voting place location in votingplace.xml is not a unique voting place; there can be multiple voting places using the same ID. The reason for this is that **election day and advance voting places use different voting place numbers**. On election day, voting materials are all new; new ballot pads, new issuing point stamps, new special declaration forms etc. The election day voting place has a different number from the advance voting place that was set up at the same location, and results will come in at different times. But they will share the same location ID. The location ID is the `id` attribute and the electorate-specific voting place number is the `voting_place_id` attribute of `VotingPlaceResult`.
  * Voting places are numbered within their electorate (but their location ID is unique nationwide; it isn't scoped to that electorate). This means that there might be a voting place 004 in both Auckland Central and Wellington Central, for example. 
  * Voting places numbered 0xx are election day voting places. 2xx are advance voting places. 3xx seem to be mobile teams (prisons, rest homes, hospitals etc). This isn't in the specifications so it could change; but if you want to work it out for yourself: generally there are more election day voting places than advance voting places, and more advance voting places than mobile teams.
  * The HTML index page for the /eNN/votingplaces/ directory doesn't list every voting place in the electorate; some are hidden. So don't be surprised if the count says that 40 voting places have been counted but you only have results for 37.
  * The specifications say that there won't be a voting place result file created until results actually come in (they say this about the electorate file too). This was the case at the Hamilton West by-election. But at the Tauranga by-election, this wasn't true and there were results files with 0s for totals for every voting place before the results started coming in. In my opinion, the latter approach is better because then you know which voting places you can actually expect results for.
  * It's always good to remember that a voting place doesn't necessarily just issue ordinary votes for the electorate it's based in. It will issue ordinary votes for its general electorate, its Māori electorate, and maybe a neighbouring electorate. Or even electorates further afield; voting places at universities issue ordinary votes for many electorates. 
