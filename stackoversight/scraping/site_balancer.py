import logging

from stackoversight.scraping.release_heap import AbstractReleaseHeap


# really just a wrapper for ReleaseHeap, designed for client_ids to be iterated through
class SiteBalancer(AbstractReleaseHeap):

    def __init__(self, sessions: list, timeout_sec: int, limit=None):
        self.limit = limit
        super().__init__(sessions, timeout_sec)

    # capture signal should be sent after using the client_id, so the call is not included here
    def __next__(self):
        with self.heap_lock.read_lock:
            if self.limit and self.heap[0][0] >= self.limit:
                logging.warning(f'Limit reached for client key {self.heap[0][1]}')

                raise StopIteration

            client_id = self.heap[0][1]

        return client_id

    def update_ready(self):
        with self.heap_lock.read_lock:
            if not self.limit or self.heap[0][0] < self.limit:
                self.ready.set()
            else:
                self.ready.clear()
