from redis import Redis
from dotenv import load_dotenv
import os


class RedisConnection:
    __instance = None

    @staticmethod
    def get_instance():
        """
        Static access method.
        """

        if RedisConnection.__instance is None:
            RedisConnection()
        return RedisConnection.__instance

    def __init__(self):
        """
        Virtually private constructor.
        """

        if RedisConnection.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            RedisConnection.__instance = self

        load_dotenv(verbose=True)

        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = os.getenv("REDIS_PORT", "6379")
        redis_password = os.getenv("REDIS_PASSWORD", "")
        self.redis = Redis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

    def set(self, key, value):
        self.redis.set(key, value)

    def get(self, key):
        return self.redis.get(key)

    def exists(self, key):
        return self.get(key)
