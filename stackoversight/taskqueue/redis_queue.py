from redis import Redis
from rq import Queue
from dotenv import load_dotenv
import os


class RedisQueue:
    __instance = None

    @staticmethod
    def get_instance():
        """
        Static access method.
        """

        if RedisQueue.__instance is None:
            RedisQueue()
        return RedisQueue.__instance

    def __init__(self):
        """
        Virtually private constructor.
        """

        if RedisQueue.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            RedisQueue.__instance = self

        load_dotenv(verbose=False)

        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = os.getenv("REDIS_PORT", "6379")
        redis_password = os.getenv("REDIS_PASSWORD", "")
        self.q = Queue(connection=Redis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True))
        self.job = None

    def enqueue(self, function, *args):
        self.job = self.q.enqueue(function, args)
        return self.job
