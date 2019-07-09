import os
from redis import Redis
from rq import Queue, Connection
from rq.worker import Worker
from dotenv import load_dotenv


class RedisWorker:
    def __init__(self):
        load_dotenv(verbose=True)

        listen = ['high', 'default', 'low']
        redis_host = os.getenv("REDIS_HOST") if os.getenv("REDIS_HOST") is not None else "localhost"
        redis_port = os.getenv("REDIS_PORT") if os.getenv("REDIS_PORT") is not None else 6379
        redis_password = os.getenv("REDIS_PASSWORD") if os.getenv("REDIS_PASSWORD") is not None else ""
        conn = Redis(host=redis_host, port=redis_port, password=redis_password, db=0)
        with Connection(conn):
            self.worker = Worker(map(Queue, listen))

    def work(self):
        self.worker.work()
