"""
core/config.py
Central configuration object for the whole framework.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict


DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]


@dataclass
class Config:
    timeout: int = 15
    max_retries: int = 3
    retry_backoff: float = 1.5
    delay_between_requests: float = 1.0
    concurrency: int = 4

    respect_robots_txt: bool = True
    rotate_user_agent: bool = True
    verify_ssl: bool = True

    headers: Dict[str, str] = field(default_factory=dict)
    proxies: Optional[Dict[str, str]] = None

    output_dir: str = "output"
    log_level: str = "INFO"
    animations: bool = True   # toggle hacker-style animations

    def build_headers(self) -> Dict[str, str]:
        import random
        headers = dict(self.headers)
        if "User-Agent" not in headers:
            headers["User-Agent"] = (
                random.choice(DEFAULT_USER_AGENTS)
                if self.rotate_user_agent
                else DEFAULT_USER_AGENTS[0]
            )
        headers.setdefault("Accept-Language", "en-US,en;q=0.9")
        return headers
