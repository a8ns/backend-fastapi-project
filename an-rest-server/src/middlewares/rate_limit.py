# from fastapi import Request, HTTPException
# from datetime import datetime, timedelta
# from redis import Redis as r
# import redis

# RATE_LIMIT = 100  # Number of allowed requests
# TIME_WINDOW = timedelta(minutes=10)  # Time window for the rate limit

# async def rate_limit_middleware(request: Request, call_next):
#     client_ip = request.client.host
#     current_time = datetime.now()

#     # Key structure: "rate_limit:<client_ip>:<current_time_window>"
#     current_time_window = current_time.timestamp() // TIME_WINDOW.total_seconds()
#     key = f"rate_limit:{client_ip}:{int(current_time_window)}"
    
#     # Increment the request count for this IP and time window
#     try:
#         current_request_count = r.incr(key, 1)
#         # Set the key to expire after the time window is over
#         if current_request_count == 1:
#             r.expire(key, int(TIME_WINDOW.total_seconds()))
#     except redis.RedisError:
#         # In case of Redis issues, allow the request but log the error
#         # You might want to handle this differently based on your requirements
#         current_request_count = 1

#     if current_request_count > RATE_LIMIT:
#         raise HTTPException(status_code=429, detail="Too many requests")

#     response = await call_next(request)
#     return response
