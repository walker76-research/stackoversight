# For load balancing client ids
import heapq
# For site class info
from stackoversight.scraping.site.Site import *
# For release timers
import threading
# For the release queue
import queue


class ReleaseHeap(queue):
    def __init__(self, heap: heapq, time_sec: int):
        self.heap = heap
        self.time_sec = time_sec

        # really hope this is by reference like i read, if not this wont work at all
        self.hash_map = dict([(pair[1], pair) for pair in self.heap])

    def capture(self, id: int):
        # pop off the top of the heap and increment the first value of the tuple
        pair = heapq.heappop(self.heap)
        pair[0] = pair[0] + 1
        heapq.heappush(pair)

        # put the client id into the queue
        super.put(pair[1])

        threading.Timer(self.time_sec, self.release)

    def release(self):
        top_id = super.get()
        pair = self.hash_map[top_id]

        if pair[0]:
            pair[0] = pair[0] - 1
        else:
            raise ValueError


class SiteBalancer(object):
    def __init__(self, client_ids: list, timeout_sec: int):
        # put count first since by default tuples' first element is given sorting priority
        self.client_heap = ReleaseHeap(heapq.heapify([(0, id) for id in client_ids]), timeout_sec)

    def mark_request(self):
        self.client_heap.capture()

    def peek_top_count(self):
        return self.client_heap.heap[0][0]

    def peek_top_client_id(self):
        return self.client_heap.heap[0][1]