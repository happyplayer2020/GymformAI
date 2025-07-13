import time
from collections import defaultdict
from typing import Dict, List
from app.core.config import settings

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests_per_minute = defaultdict(list)
        self.requests_per_day = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> bool:
        """
        Check if request is allowed based on rate limits
        
        Args:
            client_ip: Client IP address
            
        Returns:
            True if request is allowed, False otherwise
        """
        current_time = time.time()
        
        # Clean old entries
        self._clean_old_entries(client_ip, current_time)
        
        # Check minute limit
        minute_requests = len(self.requests_per_minute[client_ip])
        if minute_requests >= settings.RATE_LIMIT_PER_MINUTE:
            return False
        
        # Check day limit
        day_requests = len(self.requests_per_day[client_ip])
        if day_requests >= settings.RATE_LIMIT_PER_DAY:
            return False
        
        # Add current request
        self.requests_per_minute[client_ip].append(current_time)
        self.requests_per_day[client_ip].append(current_time)
        
        return True
    
    def _clean_old_entries(self, client_ip: str, current_time: float):
        """Remove old entries from tracking"""
        # Clean minute entries (older than 60 seconds)
        minute_ago = current_time - 60
        self.requests_per_minute[client_ip] = [
            req_time for req_time in self.requests_per_minute[client_ip]
            if req_time > minute_ago
        ]
        
        # Clean day entries (older than 24 hours)
        day_ago = current_time - 86400
        self.requests_per_day[client_ip] = [
            req_time for req_time in self.requests_per_day[client_ip]
            if req_time > day_ago
        ]
    
    def get_remaining_requests(self, client_ip: str) -> Dict[str, int]:
        """Get remaining requests for client"""
        current_time = time.time()
        self._clean_old_entries(client_ip, current_time)
        
        minute_remaining = max(0, settings.RATE_LIMIT_PER_MINUTE - len(self.requests_per_minute[client_ip]))
        day_remaining = max(0, settings.RATE_LIMIT_PER_DAY - len(self.requests_per_day[client_ip]))
        
        return {
            "minute_remaining": minute_remaining,
            "day_remaining": day_remaining
        } 