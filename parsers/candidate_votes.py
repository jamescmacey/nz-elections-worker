


from bs4.element import Tag

class CandidateVote:
    id: int = None
    votes: int = None

    def __init__(self, soup: Tag):
        self.id = int(soup.attrs["c_no"])
        self.votes = int(soup.find("votes").text)

    def as_dict(self) -> dict:
        return {
            "_id": self.id,
            "id": self.id,
            "votes": self.votes
        }

class CandidateVotes(list):
    def __init__(self, soup: Tag):
        votes = soup.find_all("candidate")
        for v in votes:
            self.append(CandidateVote(v))

    def as_dict(self) -> list:
        return [x.as_dict() for x in self]