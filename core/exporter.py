"""
core/exporter.py
Save scraped data to disk: JSON, CSV, TXT, XML sitemap.
"""

import json
import csv
import os
from typing import List, Dict, Any
from xml.sax.saxutils import escape


def _ensure_dir(filepath: str):
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)


def save_json(data: Any, filepath: str, indent: int = 2):
    _ensure_dir(filepath)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def save_csv(data: List[Dict[str, Any]], filepath: str):
    if not data:
        raise ValueError("No data to write to CSV")
    _ensure_dir(filepath)
    fieldnames = list({key for row in data for key in row.keys()})
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def save_txt(lines: List[str], filepath: str):
    _ensure_dir(filepath)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(str(l) for l in lines))


def save_sitemap_xml(urls: List[str], filepath: str):
    _ensure_dir(filepath)
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        parts.append(f"  <url><loc>{escape(url)}</loc></url>")
    parts.append("</urlset>")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
