import time
from django.core.cache import cache
from django.http import JsonResponse


class RateLimitingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("-- RateLimitingMiddleware triggered --")

        # Use user ID if logged in, else use IP address
        user = getattr(request, "user", None)
        ip = request.META.get("REMOTE_ADDR")
        identifier = str(user.id) if user and user.is_authenticated else ip

        # Rate limit config
        max_requests = 100
        key = f"rl:{identifier}"
        now = time.time()

        data = cache.get(key, {"count": 0, "timestamp": now})

        # Reset count if time window passed
        if now - data["timestamp"] > 60:
            data = {"count": 0, "timestamp": now}

        if data["count"] >= max_requests:
            print("Rate limit exceeded:", identifier)
            return JsonResponse(
                {"detail": "Rate limit exceeded. Max 100 requests per minute."},
                status=429
            )

        data["count"] += 1
        cache.set(key, data, timeout=60)
        print(f"Request #{data['count']} allowed for {identifier}")

        return self.get_response(request)
    