# Need a heap ofc
import heapq
# For release timers
import threading
# For the release queue
from queue import Queue
# For writer priority
from stackoversight.scraping.read_write_Lock import RWLock


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

        self.heap_lock = RWLock()
        self.release_queue = Queue()
        self.ready = threading.Event()

        # quick access to pair by it's value
        self.hash_map = dict([(pair[1], pair) for pair in self.heap])

    def __iter__(self):
        return self.heap

    def __next__(self):
        self.heap_lock.reader_acquire()
        ret = self.heap[0][1]
        self.heap_lock.reader_release()

        return ret

    def capture(self):
        # pop off the top of the heap and increment the first value of the pair
        pair = heapq.heappop(self.heap)
        pair[0] += 1
        heapq.heappush(self.heap, pair)

        # Update ready event
        self.update_ready()

        # put the value into the queue
        self.release_queue.put(pair[1])

        # start the timer for release
        threading.Timer(self.time_sec, self.release).start()

        return pair[0]

    def release(self):
        # get the id of the next to be released and with that the pair
        top_value = self.release_queue.get()
        pair = self.hash_map[top_value]

        # beginning value can be non-zero and whatever you choose should be returned to in the end
        pair[0] -= 1

        # update heap and ready
        heapq.heapify(self.heap)
        self.update_ready()

    def update_ready(self):
        raise NotImplementedError


class ReadyReleaseHeap(ReleaseHeap):
    def update_ready(self):
        if not self.ready.is_set():
            self.ready.set()
