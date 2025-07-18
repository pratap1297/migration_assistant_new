import time
from functools import wraps
from typing import Callable
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_calls: int = 14, period: int = 60):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls outside the time window
            self.calls = [call_time for call_time in self.calls 
                         if now - call_time < self.period]
            
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.1f} seconds")
                time.sleep(sleep_time)
                self.calls = []
            
            self.calls.append(now)
            return func(*args, **kwargs)
        return wrapper