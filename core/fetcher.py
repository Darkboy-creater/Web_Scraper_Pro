"""
core/fetcher.py
Handles all HTTP communication: sessions, retries, robots.txt checks.
"""

import time
import random
import urllib.robotparser as robotparser
from urllib.parse import urljoin, urlparse
from functools import lru_cache
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .config import Config
from .logger import get_logger


@lru_cache(maxsize=64)
def _get_robot_parser(base_url: str):
    rp = robotparser.RobotFileParser()
    rp.set_url(urljoin(base_url, "/robots.txt"))
    try:
        rp.read()
    except Exception:
        return None
    return rp


def is_allowed_by_robots(url: str, user_agent: str = "*") -> bool:
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    rp = _get_robot_parser(base)
    if rp is None:
        return True
    try:
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True


class Fetcher:
    """Wraps a requests.Session with retry logic, throttling and robots.txt checks."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.logger = get_logger(level=self.config.log_level)
        self.session = requests.Session()
        self.session.headers.update(self.config.build_headers())
        if self.config.proxies:
            self.session.proxies.update(self.config.proxies)
        self._last_request_time = 0.0

    def _throttle(self):
        elapsed = time.time() - self._last_request_time
        wait = self.config.delay_between_requests - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_request_time = time.time()

    def get(self, url: str, allow_head: bool = False) -> Optional[requests.Response]:
        if self.config.respect_robots_txt and not is_allowed_by_robots(
            url, self.session.headers.get("User-Agent", "*")
        ):
            self.logger.warning(f"Blocked by robots.txt: {url}")
            return None

        self._throttle()
        attempt = 0
        backoff = self.config.retry_backoff
        method = self.session.head if allow_head else self.session.get

        while attempt <= self.config.max_retries:
            try:
                resp = method(url, timeout=self.config.timeout, verify=self.config.verify_ssl,
                               allow_redirects=True)
                if resp.status_code == 429:
                    raise requests.exceptions.RequestException("Rate limited (429)")
                resp.raise_for_status()
                return resp
            except requests.exceptions.RequestException as e:
                attempt += 1
                self.logger.warning(f"Attempt {attempt}/{self.config.max_retries} failed for {url}: {e}")
                if attempt <= self.config.max_retries:
                    time.sleep(backoff)
                    backoff *= 2
        self.logger.error(f"Giving up on {url}")
        return None

    def fetch_soup(self, url: str, parser: str = "html.parser") -> Optional[BeautifulSoup]:
        resp = self.get(url)
        if resp is None:
            return None
        return BeautifulSoup(resp.text, parser)

    def status_of(self, url: str) -> Optional[int]:
        """Cheap check (HEAD request) — used by the broken-link checker."""
        try:
            self._throttle()
            resp = self.session.head(url, timeout=self.config.timeout, allow_redirects=True)
            return resp.status_code
        except requests.exceptions.RequestException:
            try:
                resp = self.session.get(url, timeout=self.config.timeout, stream=True)
                return resp.status_code
            except requests.exceptions.RequestException:
                return None

    def close(self):
        self.session.close()
