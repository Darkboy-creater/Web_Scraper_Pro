"""
core/extractors.py
All extraction logic lives here: text, links, images, emails, phones,
social links, meta tags, tables, forms, keyword frequency, structured data.
"""

import re
from collections import Counter
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s.\-]?)?(\(?\d{2,4}\)?[\s.\-]?)?\d{3,4}[\s.\-]?\d{3,4}")
SOCIAL_DOMAINS = [
    "facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com",
    "youtube.com", "tiktok.com", "pinterest.com", "t.me", "wa.me", "github.com",
    "reddit.com", "threads.net",
]

STOPWORDS = set("""
a an the is are was were be been being to of in on for with as by at from
and or but if then so this that these those it its it's you your we our
i my he she they them his her their not no yes do does did can will would
should could has have had than too very just about into over under more
most other some such only own same s t don now
""".split())


# ------------------------------------------------------------------ #
# 1. Page info
# ------------------------------------------------------------------ #
def get_page_info(soup, response) -> Dict:
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else None
    h1s = [h.get_text(strip=True) for h in soup.find_all("h1")]
    lang = soup.html.get("lang") if soup.html else None

    return {
        "title": title,
        "description": description,
        "h1_tags": h1s,
        "language": lang,
        "status_code": response.status_code if response is not None else None,
        "content_length": len(response.text) if response is not None else None,
        "final_url": response.url if response is not None else None,
    }


# ------------------------------------------------------------------ #
# 2. Generic CSS selector extraction
# ------------------------------------------------------------------ #
def extract_by_selector(soup, selector: str, attr: Optional[str] = None) -> List[str]:
    elements = soup.select(selector)
    if attr:
        return [el.get(attr, "").strip() for el in elements if el.get(attr)]
    return [el.get_text(strip=True) for el in elements]


# ------------------------------------------------------------------ #
# 3. Structured (multi-field) extraction
# ------------------------------------------------------------------ #
def extract_structured(soup, item_selector: str, fields: Dict[str, str]) -> List[Dict]:
    results = []
    for item in soup.select(item_selector):
        record = {}
        for key, sub_selector in fields.items():
            el = item.select_one(sub_selector)
            record[key] = el.get_text(strip=True) if el else None
        results.append(record)
    return results


# ------------------------------------------------------------------ #
# 4. Links
# ------------------------------------------------------------------ #
def extract_links(soup, base_url: str, internal_only: bool = False) -> List[str]:
    links = []
    base_domain = urlparse(base_url).netloc
    for a in soup.select("a[href]"):
        href = urljoin(base_url, a["href"])
        if href.startswith("http"):
            if internal_only and urlparse(href).netloc != base_domain:
                continue
            links.append(href)
    return list(dict.fromkeys(links))


# ------------------------------------------------------------------ #
# 5. Images
# ------------------------------------------------------------------ #
def extract_images(soup, base_url: str) -> List[str]:
    images = []
    for img in soup.select("img[src]"):
        images.append(urljoin(base_url, img["src"]))
    return list(dict.fromkeys(images))


# ------------------------------------------------------------------ #
# 6. Emails
# ------------------------------------------------------------------ #
def extract_emails(text: str) -> List[str]:
    return sorted(set(EMAIL_RE.findall(text)))


# ------------------------------------------------------------------ #
# 7. Phone numbers
# ------------------------------------------------------------------ #
def extract_phones(text: str) -> List[str]:
    candidates = PHONE_RE.findall(text)
    joined = PHONE_RE.finditer(text)
    numbers = set()
    for m in joined:
        val = m.group().strip()
        digits = re.sub(r"\D", "", val)
        if 7 <= len(digits) <= 15:
            numbers.add(val)
    return sorted(numbers)


# ------------------------------------------------------------------ #
# 8. Social media links
# ------------------------------------------------------------------ #
def extract_social_links(links: List[str]) -> Dict[str, List[str]]:
    found = {}
    for link in links:
        domain = urlparse(link).netloc.replace("www.", "")
        for social in SOCIAL_DOMAINS:
            if social in domain:
                found.setdefault(social, []).append(link)
    return found


# ------------------------------------------------------------------ #
# 9. Meta tags
# ------------------------------------------------------------------ #
def extract_meta_tags(soup) -> List[Dict[str, str]]:
    metas = []
    for tag in soup.find_all("meta"):
        metas.append(dict(tag.attrs))
    return metas


# ------------------------------------------------------------------ #
# 10. Tables
# ------------------------------------------------------------------ #
def extract_tables(soup) -> List[List[List[str]]]:
    all_tables = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
            if cells:
                rows.append(cells)
        if rows:
            all_tables.append(rows)
    return all_tables


# ------------------------------------------------------------------ #
# 11. Forms
# ------------------------------------------------------------------ #
def extract_forms(soup, base_url: str) -> List[Dict]:
    forms = []
    for form in soup.find_all("form"):
        action = urljoin(base_url, form.get("action", ""))
        method = form.get("method", "GET").upper()
        inputs = []
        for inp in form.find_all(["input", "select", "textarea"]):
            inputs.append({
                "tag": inp.name,
                "name": inp.get("name"),
                "type": inp.get("type", "text") if inp.name == "input" else inp.name,
            })
        forms.append({"action": action, "method": method, "fields": inputs})
    return forms


# ------------------------------------------------------------------ #
# 12. Keyword / word frequency
# ------------------------------------------------------------------ #
def keyword_frequency(soup, top_n: int = 20) -> List[Dict]:
    text = soup.get_text(" ", strip=True).lower()
    words = re.findall(r"[a-zA-Z']{3,}", text)
    words = [w for w in words if w not in STOPWORDS]
    counts = Counter(words)
    return [{"word": w, "count": c} for w, c in counts.most_common(top_n)]


# ------------------------------------------------------------------ #
# 13. Files by extension (pdf, docx, zip, etc.)
# ------------------------------------------------------------------ #
def find_files_by_extension(soup, base_url: str, extensions: List[str]) -> List[str]:
    exts = tuple(e.lower().lstrip(".") for e in extensions)
    found = []
    for a in soup.select("a[href]"):
        href = urljoin(base_url, a["href"])
        path = urlparse(href).path.lower()
        if path.endswith(tuple(f".{e}" for e in exts)):
            found.append(href)
    return list(dict.fromkeys(found))
