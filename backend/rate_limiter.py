import time
import threading
from typing import Dict, List, Tuple

class RateLimiter:
    """
    Thread-safe sliding-window rate limiter to protect LLM generation endpoints
    from excessive requests and cost overruns.
    """
    def __init__(self, max_requests: int = 15, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._lock = threading.Lock()
        self._history: Dict[str, List[float]] = {}

    def is_allowed(self, client_key: str = "global") -> Tuple[bool, int]:
        """
        Determines whether client is within rate limits.
        Returns (is_allowed: bool, retry_after_seconds: int).
        """
        now = time.time()
        with self._lock:
            timestamps = self._history.get(client_key, [])
            # Purge timestamps outside the window
            cutoff = now - self.window_seconds
            timestamps = [t for t in timestamps if t > cutoff]

            if len(timestamps) >= self.max_requests:
                earliest = timestamps[0]
                retry_after = max(1, int(earliest + self.window_seconds - now))
                self._history[client_key] = timestamps
                return False, retry_after

            timestamps.append(now)
            self._history[client_key] = timestamps
            return True, 0

    def reset(self, client_key: Optional[str] = None):
        with self._lock:
            if client_key:
                self._history.pop(client_key, None)
            else:
                self._history.clear()
