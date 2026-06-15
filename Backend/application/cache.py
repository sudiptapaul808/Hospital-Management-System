from redis import Redis
import json

redis_client = Redis(host="localhost", port=6379, db=2, decode_responses=True)

def cache_get(key):
    data = redis_client.get(key)
    return json.loads(data) if data else None

def cache_set(key, value, ttl=60):
    redis_client.set(key, json.dumps(value), ex=ttl)

def cache_delete(key):
    redis_client.delete(key)
    
def cache_delete_pattern(pattern):  #this is to delete all the pages for the paginated routes
    for key in redis_client.scan_iter(pattern):
        redis_client.delete(key)