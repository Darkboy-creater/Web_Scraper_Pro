"""
core/crawler.py
Multi-page crawling, sitemap generation, and broken-link checking.
"""

from collections import deque
from typing import Callable, List, Dict, Optional
from urllib.parse import urlparse

from .fetcher import Fetcher
from . import extractors


def crawl(
    fetcher: Fetcher,
    start_url: str,
    max_pages: int = 20,
    max_depth: int = 2,
    on_page: Optional[Callable] = None,
    internal_only: bool = True,
    progress_cb: Optional[Callable[[int, int, str], None]] = None,
) -> List[str]:
    """Breadth-first crawl. Calls on_page(url, soup) for every page fetched."""
    visited = set()
    queue = deque([(start_url, 0)])
    order = []

    while queue and len(order) < max_pages:
        url, depth = queue.popleft()
        if url in visited or depth > max_depth:
            continue
        visited.add(url)

        soup = fetcher.fetch_soup(url)
        if soup is None:
            continue

        order.append(url)
        if progress_cb:
            progress_cb(len(order), max_pages, url)

        if on_page:
            on_page(url, soup)

        if depth < max_depth:
            for link in extractors.extract_links(soup, url, internal_only=internal_only):
                if link not in visited:
                    queue.append((link, depth + 1))

    return order


def generate_sitemap(
    fetcher: Fetcher,
    start_url: str,
    max_pages: int = 50,
    max_depth: int = 3,
    progress_cb: Optional[Callable[[int, int, str], None]] = None,
) -> List[str]:
    """Crawl a site and return the list of discovered internal URLs (for sitemap.xml)."""
    return crawl(
        fetcher, start_url, max_pages=max_pages, max_depth=max_depth,
        internal_only=True, progress_cb=progress_cb,
    )


def check_broken_links(
    fetcher: Fetcher,
    links: List[str],
    progress_cb: Optional[Callable[[int, int, str], None]] = None,
) -> List[Dict]:
    """Check each link's HTTP status. Returns list of {url, status, broken}."""
    results = []
    for i, link in enumerate(links, 1):
        status = fetcher.status_of(link)
        broken = status is None or status >= 400
        results.append({"url": link, "status": status, "broken": broken})
        if progress_cb:
            progress_cb(i, len(links), link)
    return results
