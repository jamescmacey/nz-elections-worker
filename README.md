# election-results-manager
Contains dataclasses and MongoDB interfaces for election results. It pulls election results in XML format from the Electoral Commission's results site.

This is the worker used to generate the results for https://elections.wheretheystand.nz.

## Election night worker
The worker can link into the Electoral Commission's XML-based Media Feed for the ingest of results on election night.
* For by-elections, you only need one worker.
* For general elections, unless you want only electorate level (not voting place level) results, you need two workers. One will just do national results and electorate results; the other will be working almost non-stop to pull voting place results. In 2023 I didn't actually bother with live voting place results—but this is how you would do it.

### Rollback prevention
Due to caching, occasionally the Electoral Commission's servers will serve results files which are outdated (i.e. datestamped earlier than a file that has already been served). By default, this worker guards against this and will only process results files which are newer than the ones it has already ingested.

## Dataclasses

### Events
These can be either an election or a poll. The data structure is essentially the same.

### Poll Series (not properly implemented)
Groups a collection of polls e.g. 1News Verian, or Newshub Reid Research.

### Result Sets
Stores the actual results. These are linked to the event through the `event_id`, can be at one of three levels (`"national"`, `"electorate"`, or `"voting_place"`), and can be one of two types (`"party"` or `"candidate"`).

Advance voting places and an election day voting places, even if they take place at the same location, have been considered separate voting places in the Electoral Commission's results system. In 2023 the Media Feed appeared to sum these results into one file, but, in other places, they were reported separately (e.g. in the PDF/CSV electorate summaries). Past elections certainly had separate files for each, so the code here is built to deal with either scenario. 

The `"electorate"` level of results combines all `"voting_place"` results for a given electorate and results type. 

The `"national"` level of results combines all `"electorate"` results for the results type `"party"`.

Be aware that, as scraping of results is asynchronous, there may be times during live events where the election file is not a perfect aggregate of the election files, etc.

### Election Candidates
A collection of candidates. Each candidate is scoped to the relevant election they were a candidate in through the `event_id`. 

### Election Parties
A collection of parties. Each party is scoped to the relevant election they were a party in through the `event_id`. 

### Election Voting Places
A collection of voting places. Each voting placce is scoped to the relevant election it was a voting place in through the `event_id`. 

### Election Electorates
A collection of electorates. Each electorate is scoped to the relevant election it was an electorate in through the `event_id`. 

### Persistent Candidates
Provides a globally unique reference object for a candidate which does not change between elections. This means that the same candidate can be tracked across elections, even if the candidate stands in another electorate or for another party.

### Persistent Parties
Provides a globally unique reference object for a party which does not change between elections.

### Persistent Electorates
Provides a globally unique reference object for an electorate which does not change between elections.

### Persistent Voting Places
Provides a globally unique reference object for an electorate which does not change between elections.

Even where voting places are set up at the same locations in multiple elections, it seems that the coordinates are not always the same. To match voting places between elections, a distance threshold is used. Voting places . **Note**: In some cases, there will be multiple Election Voting Places for the same event using the same Persistent Voting Place. For example: a local community centre has an advance voting place in one small room, but, on election day, the voting place is in a different, larger room at the same facility. In some cases these are set up as separate voting places, but given both will be very close together, they will likely match to the same persistent voting place. 