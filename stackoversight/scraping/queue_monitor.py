from threading import Thread
from queue import Queue


class QueueMonitor(Thread):
    def __init__(self, queue: Queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        self.queue.join()
