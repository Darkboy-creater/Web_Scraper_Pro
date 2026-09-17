"""
core/downloader.py
Handles downloading images and files (pdf, docx, zip, etc.) to disk.
"""

import os
import time
from typing import List, Dict, Callable, Optional
from urllib.parse import urlparse


def _safe_filename(url: str, index: int, default_ext: str = ".bin") -> str:
    path = urlparse(url).path
    name = os.path.basename(path) or f"file_{index}{default_ext}"
    if "." not in name:
        name += default_ext
    name = "".join(c for c in name if c.isalnum() or c in "._-")[:80]
    return f"{index}_{name}"


def download_urls(
    session,
    urls: List[str],
    out_dir: str,
    limit: int = 20,
    delay: float = 0.4,
    progress_cb: Optional[Callable[[int, int, str, bool], None]] = None,
) -> Dict:
    """
    Download a list of URLs to out_dir.
    Returns {"downloaded": int, "failed": int, "files": [paths]}.
    """
    os.makedirs(out_dir, exist_ok=True)
    urls = urls[:limit]
    downloaded, failed, files = 0, 0, []

    for i, url in enumerate(urls, 1):
        ok = False
        try:
            resp = session.get(url, timeout=15, stream=True)
            resp.raise_for_status()
            fname = _safe_filename(url, i)
            fpath = os.path.join(out_dir, fname)
            with open(fpath, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            downloaded += 1
            files.append(fpath)
            ok = True
        except Exception:
            failed += 1
        finally:
            if progress_cb:
                progress_cb(i, len(urls), url, ok)
            time.sleep(delay)

    return {"downloaded": downloaded, "failed": failed, "files": files}
