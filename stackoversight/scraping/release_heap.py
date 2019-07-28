import heapq
import logging
import threading
from queue import Queue

from stackoversight.scraping.read_write_Lock import RWLock


class AbstractReleaseHeap(object):
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
        self.queue_lock = threading.Lock()
        self.release_queue = Queue()
        self.ready = threading.Event()

        # update and make sure the keys are under the limit
        self.update_ready()
        if not self.ready.is_set():
            logging.critical('The keys used to initialize are already over the request limit!'
                             'Can\'t initialize properly, raising exception.')
            raise ValueError

        # quick access to pair by it's value
        self.hash_map = dict([(pair[1], pair) for pair in self.heap])

    def __iter__(self):
        return self.heap

    def __next__(self):
        with self.heap_lock.read_lock:
            ret = self.heap[0][1]

        return ret

    def capture(self):
        # pop off the top of the heap and increment the first value of the pair
        with self.heap_lock.write_lock:
            pair = heapq.heappop(self.heap)
            pair[0] += 1
            heapq.heappush(self.heap, pair)

        # Update ready event
        self.update_ready()

        # put the value into the queue
        with self.queue_lock:
            self.release_queue.put(pair[1])

        # start the timer for release
        threading.Timer(self.time_sec, self.release).start()

        return pair[0]

    def release(self):
        # get the id of the next to be released and with that the pair
        with self.queue_lock:
            top_value = self.release_queue.get()
        pair = self.hash_map[top_value]

        # update heap and ready
        with self.heap_lock.write_lock:
            # beginning value can be non-zero and whatever you choose should be returned to in the end
            pair[0] -= 1
            heapq.heapify(self.heap)

        self.update_ready()

    def update_ready(self):
        raise NotImplementedError


class ReadyReleaseHeap(AbstractReleaseHeap):
    def update_ready(self):
        if not self.ready.is_set():
            self.ready.set()
