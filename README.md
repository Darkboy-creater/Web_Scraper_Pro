# Web Scraper Pro v2.0 — Termux Edition

Ek complete, modular web scraping framework — `core/` folder me saare modules alag-alag, professional hacker-style boot sequence + animated banner ke saath, aur **18 built-in features**.

**v2.0 fixes:** `lxml` dependency hata di gayi (kabhi use hi nahi ho rahi thi, aur Termux pe compile fail karke pura install hi tod deti thi). Banner ab pure ASCII hai — kisi bhi Termux font pe sahi render hoga. Startup pe ek real "hacker tool" boot checklist bhi hai.
*KALI LINUX* interface 
<img width="1610" height="670" alt="Image" src="https://github.com/user-attachments/assets/539b4c41-4f9e-444d-af32-cc802d7cd5b4" />

#TERMUX INTERFACE 
<img width="720" height="1612" alt="Image" src="https://github.com/user-attachments/assets/11d64923-16a6-4373-a73d-18de8f7e5212" />

```
webscraper_pro/
├── main.py               # Entry point — banner, menu, sab kuch wire karta hai
├── requirements.txt
├── README.md
└── core/                  # Sab logic yaha hai
    ├── __init__.py
    ├── config.py            # Settings (Config dataclass)
    ├── logger.py             # Colored logging
    ├── fetcher.py              # HTTP requests, retries, robots.txt check
    ├── extractors.py            # 13 extraction functions
    ├── crawler.py                 # Multi-page crawl, sitemap, broken-link check
    ├── downloader.py                # Image/file downloader
    ├── exporter.py                   # JSON/CSV/TXT/XML export
    └── ui.py                          # Banner, matrix animation, spinner, progress bar
```

---

## 1. Termux Setup

```bash
pkg update && pkg upgrade -y
pkg install python -y
pkg install git -y
git clone https://github.com/Darkboy-creater/Web_Scraper_Pro.git
cd Web_Scraper_Pro
ls
pip install -r requirements.txt
```

Sirf 2 lightweight dependencies (`requests`, `beautifulsoup4`) — koi compile-heavy package nahi, install 10-15 second me ho jayega.

## 2. Run

```bash
python start.py
```

Launch hote hi:
1. Ek **module boot checklist** chalti hai (`[OK] Loading core.fetcher` type)
2. Fir ek short **ASCII matrix-rain animation**
3. Fir professional **boxed banner**
4. Fir grouped menu (18 features, 4 categories me)

---

## 3. All 18 Features

### Page Analysis
1. **Page Info** — title, meta description, H1 tags, status code, language
2. **Extract by CSS Selector** — koi bhi selector + optional attribute (href, src, etc.)
3. **Extract Structured Data** — multi-field records (e.g. product cards: title+price+image)
4. **Extract All Meta Tags** — full meta tag dump
5. **Extract Tables → CSV** — HTML tables ko seedha CSV me convert
6. **Extract Forms** — form action, method, aur saare input fields
7. **Keyword Frequency Analysis** — page ke top keywords (stopwords hata ke)

### Links & Media
8. **Extract All Links** — internal/external filter ke saath
9. **Extract Social Media Links** — Facebook, Instagram, Twitter/X, LinkedIn, YouTube, etc.
10. **List All Images** — saari image URLs
11. **Download Images** — progress bar ke saath bulk download
12. **Download Files by Extension** — pdf, docx, zip, etc.

### Contact Info
13. **Extract Emails** — regex-based email finder
14. **Extract Phone Numbers** — pattern-based (verify manually, false positives possible)

### Site-Wide
15. **Crawl Multiple Pages** — BFS crawl with depth limit
16. **Generate Sitemap (XML)** — pura site crawl karke `sitemap.xml` banata hai
17. **Broken Link Checker** — saare links ka status code check (404, 500, etc.)
18. **Full Page Report** — sab kuch ek saath run karke ek consolidated JSON report

Har feature ka output `output/` folder me save hota hai.

---

## 4. Module Overview (`core/`)

| Module | Kaam |
|---|---|
| `config.py` | Timeout, retries, delay, User-Agent rotation, proxy, animations toggle |
| `fetcher.py` | `Fetcher` class — retry+backoff, robots.txt respect, throttling |
| `extractors.py` | Saari extraction logic — 13 standalone functions |
| `crawler.py` | BFS crawl, sitemap generation, broken-link checker |
| `downloader.py` | Bulk image/file download with progress callback |
| `exporter.py` | JSON / CSV / TXT / XML sitemap save karna |
| `ui.py` | Colors, matrix intro, typewriter banner, spinner, progress bar |
| `logger.py` | Colored console logging |

---

## 5. Use as a Library (apne script me import karke)

```python
from core import Config, Fetcher, extractors, exporter

cfg = Config(delay_between_requests=1.0)
fx = Fetcher(cfg)

soup = fx.fetch_soup("https://example.com")
titles = extractors.extract_by_selector(soup, "h2.title")
exporter.save_json(titles, "output/titles.json")

fx.close()
```

---

## 6. Config Options (`core/config.py`)

| Field | Default | Description |
|---|---|---|
| `timeout` | 15 | Request timeout (s) |
| `max_retries` | 3 | Retry attempts |
| `retry_backoff` | 1.5 | Backoff multiplier |
| `delay_between_requests` | 1.0 | Politeness delay |
| `respect_robots_txt` | True | Robots.txt honor karna |
| `rotate_user_agent` | True | Random UA per session |
| `animations` | True | Matrix intro + typewriter banner on/off |
| `proxies` | None | `{"https": "http://ip:port"}` |

Animations band karne ke liye: `Config(animations=False)`.

---

## 7. Best Practices

- Kisi bhi site ka `robots.txt` aur Terms of Service respect karo.
- `delay_between_requests` kabhi 0 mat rakho.
- Ye framework sirf static HTML parse karta hai — JS-heavy (React/Vue SPA) sites ke liye kaam nahi karega, kyunki Termux me headless browser chalana heavy hai.
- Bina permission ke private/personal data scrape mat karo.

---

Happy hacking! 🕶️🐍
