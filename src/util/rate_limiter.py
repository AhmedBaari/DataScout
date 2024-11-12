import time

class RateLimiter:
    def __init__(self, max_requests, interval):
        self.max_requests = max_requests
        self.interval = interval
        self.requests = 0
        self.start_time = time.time()

    def is_allowed(self):
        current_time = time.time()
        if current_time - self.start_time > self.interval:
            self.start_time = current_time
            self.requests = 0
        if self.requests < self.max_requests:
            self.requests += 1
            return True
        return False

