# Data structure for balancing
from stackoversight.scraping.release_heap import ReleaseHeap


# really just a wrapper for ReleaseHeap, designed for client_ids to be iterated through
class SiteBalancer(ReleaseHeap):
    def __init__(self, sessions: list, timeout_sec: int, limit=None):
        super().__init__(sessions, timeout_sec)
        self.limit = limit

    # capture signal should be sent after using the client_id, so the call is not included here
    def __next__(self):
        if self.limit and self.heap[0][0] >= self.limit:
            raise StopIteration

        client_id = self.heap[0][1]
        return client_id

    def is_ready(self):
        return not self.limit or self.heap[0][0] < self.limit
