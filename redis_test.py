from stackoversight.redis import RedisConnection

redis = RedisConnection.get_instance()
redis.set("key", "Hello World")
msg = redis.get("key")
print(msg)