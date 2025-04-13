import logging
from datetime import datetime
import os

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file = os.path.join(LOG_DIR, "ip_log.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    filemode="a",
)


class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get("REMOTE_ADDR")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"IP: {ip} | Time: {timestamp}")
        return self.get_response(request)
    