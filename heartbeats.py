from dataclasses import dataclass
from datetime import datetime
import zoneinfo

@dataclass
class Heartbeat:
    worker_id: str
    event_id: str
    status: str
    datetime: datetime = None
    datetime_timestamp: float = None

    def __init__(self, worker_id, event_id, status):
        self.worker_id = worker_id
        self.event_id = event_id
        self.status = status
        self.datetime = datetime.now(zoneinfo.ZoneInfo("Pacific/Auckland"))
        self.datetime_timestamp = self.datetime.timestamp()

    def send(self):
        try:
            from utils import get_db_handle
            db = get_db_handle()
            db.heartbeat.insert_one(self.__dict__)
        except:
            print("HEARTBEAT Could not send heartbeat.")