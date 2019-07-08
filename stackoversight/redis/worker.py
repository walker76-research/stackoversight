import os
from redis import Redis
from rq import Queue, Connection
from rq.worker import Worker
from dotenv import load_dotenv


class RedisWorker:
    def __init__(self):
        load_dotenv(verbose=True)

        listen = ['high', 'default', 'low']
        redis_host = os.getenv("REDIS_HOST")
        redis_port = os.getenv("REDIS_PORT")
        redis_password = os.getenv("REDIS_PASSWORD")
        conn = Redis(host=redis_host, port=redis_port, password=redis_password, db=0)
        with Connection(conn):
            self.worker = Worker(map(Queue, listen))

    def work(self):
        self.worker.work()
