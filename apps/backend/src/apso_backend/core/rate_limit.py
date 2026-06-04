from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from threading import Lock
from time import monotonic


@dataclass
class RateLimiter:
    max_requests: int
    window_seconds: int
    buckets: dict[str, deque[float]] = field(default_factory=lambda: defaultdict(deque))
    lock: Lock = field(default_factory=Lock)

    def allow(self, key: str) -> tuple[bool, int]:
        now = monotonic()
        cutoff = now - self.window_seconds
        with self.lock:
            bucket = self.buckets[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            remaining = max(self.max_requests - len(bucket), 0)
            if len(bucket) >= self.max_requests:
                return False, 0
            bucket.append(now)
            return True, max(remaining - 1, 0)
