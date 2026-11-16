import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timezone

class SlidingWindowLimiter:
    """Allow at most 'limit' hits per 'window' seconds, per key"""

    def __init__(self, limit:int, window:float):
        self.limit=limit
        self.window=window
        self.hits=defaultdict(deque)
        self.lock=threading.Lock()

    def allow(self, key:str)->bool:
        now=time.monotonic()

        with self.lock:
            if len(self.hits)>5000:
                stale=[k for k, q in self.hits.items() if not q or now -q[-1]>  self.window]

                for k in stale:
                    del self.hits[k]

        q=self.hits[key]
        while q and now -q[0]>self.window:
            q.popleft()
        if len(q)>=self.limit:
            return False
        q.append(now)
        return True


class DailyCap:
    """Allow at most 'limit' hits per UTC day, across all users."""

    def __init__(self, limit:int):
        self.limit=limit
        self.day=datetime.now(timezone.utc).date()
        self.count=0
        self.lock=threading.Lock()

    def allow(self)->bool:
        today=datetime.now(timezone.utc).date()
        with self.lock:
            if today != self.day:
                self.day, self.count=today, 0
            if self.count>=self.limit:
                return False
            self.count+=1
            return True