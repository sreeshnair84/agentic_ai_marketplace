import redis.asyncio as redis
import asyncio

async def test_redis():
    r = redis.Redis.from_url('redis://localhost:6379/0')
    await r.ping()
    print('Redis connection successful!')
    await r.aclose()

if __name__ == "__main__":
    asyncio.run(test_redis())
