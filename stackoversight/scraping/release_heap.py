# Need a heap ofc
import heapq
# For release timers
import threading
# For the release queue
from queue import Queue


class ReleaseHeap(object):
    """
        elem_list must be a list of mutable tuples!
        the left value needs to be comparable and incrementable/decrementable
    """
    def __init__(self, elem_list: list, time_sec: int):
        # init the heap and queue and assign variables
        heapq.heapify(elem_list)
        self.heap = elem_list
        self.time_sec = time_sec
        self.release_queue = Queue()

        # quick access to pair by it's value
        self.hash_map = dict([(pair[1], pair) for pair in self.heap])

    def __iter__(self):
        return self.heap

    def __next__(self):
        return self.heap[0][1]

    def capture(self):
        # pop off the top of the heap and increment the first value of the pair
        pair = heapq.heappop(self.heap)
        pair[0] += 1
        heapq.heappush(self.heap, pair)

        # put the value into the queue
        self.release_queue.put(pair[1])

        # start the timer for release
        threading.Timer(self.time_sec, self.release).start()

    def release(self):
        # get the id of the next to be released and with that the pair
        top_value = self.release_queue.get()
        pair = self.hash_map[top_value]

        # beginning value can be non-zero and whatever you choose should be returned to in the end
        pair[0] -= 1
