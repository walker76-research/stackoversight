from pipeline.pipelineoutput import PipelineOutput
from taskqueue.redis_queue import RedisQueue
from taskqueue.redis_connection import RedisConnection
from redis import ConnectionError
from rq import Connection, Worker, Queue
# from queue import Queue


class Pipeline(object):

    __redis_initialized = False

    # Steps: The pipeline steps to accomplish
    # Redis_key: unknown
    # Items: Initial queue of code snippets
    def __init__(self, steps=None):
        if steps is None:
            steps = []
        self.steps = steps
        self.redis_instance = RedisConnection()
        self.redis_queue = RedisQueue.get_instance()
        self.__queues = []
        for step in steps:
            self.__queues.append(Queue(name=step.name, connection=self.redis_instance.redis))

    # TODO: Make this asynchronous to launch multiple workers at once
    def setup_workers(self):
        print(self.__queues)
        try:
            with Connection():
                workers = []
                for ind, step in enumerate(self.steps):
                    work = Worker([self.__queues[ind]], connection=self.redis_instance.redis,
                                  name=(self.__queues[ind].name + "_worker"))
                    workers.append(work)
                for worker in workers:
                    worker.work()
                    print("starting worker " + worker.name)
        except ConnectionError:
            print("Could not connect to host")

    def get_redis_instance(self):
        return self.redis_instance

    def set_steps(self, steps):
        self.steps = steps

    def execute_synchronous(self, items):
        # Feed the item into one step, get the result, feed the
        # result to the next step and so on.
        for step in self.steps:
            step.process(items)
            items = step.get()

        return PipelineOutput(items)
