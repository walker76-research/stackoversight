from stackoversight.redis_connection import RedisConnection

redis = RedisConnection.get_instance()
redis.set("key", "Hello World")
msg = redis.get("key")
print(msg)
