from redis import ConnectionPool

redis_pool = ConnectionPool(host="localhost", port=6379, db=0, decode_responses=True)