import time

class RateLimiter:
    def __init__(self, max_requests, interval):
        self.max_requests = max_requests
        self.interval = interval
        self.requests = []

    def is_allowed(self):
        current_time = time.time()
        self.requests = [req for req in self.requests if req > current_time - self.interval]
        if len(self.requests) < self.max_requests:
            self.requests.append(current_time)
            return True
        return False

