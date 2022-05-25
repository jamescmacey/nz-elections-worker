


from bs4.element import Tag

class CandidateVote:
    id: int = None
    votes: int = None

    def __init__(self, soup: Tag):
        self.id = int(soup.attrs["c_no"])
        self.votes = int(soup.find("votes").text)

class CandidateVotes(list):
    def __init__(self, soup: Tag):
        votes = soup.find_all("candidate")
        for v in votes:
            self.append(CandidateVote(v))