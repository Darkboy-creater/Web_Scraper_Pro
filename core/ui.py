"""
core/ui.py
Terminal UI: colors, boot sequence, animated banner, spinners, progress bars.

Design goals (v2):
  - Pure ASCII where it matters (banner art, matrix rain) so it renders
    correctly on every Termux font -- no mangled/garbled output.
  - A real "hacker tool" boot sequence: module checklist -> matrix rain
    -> boxed banner -> menu.
  - Degrades gracefully: if the terminal is very narrow (phone portrait),
    a compact banner is shown instead of the full block-letter art.
"""

import os
import sys
import time
import random
import shutil


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    GREEN = "\033[92m"
    BRIGHT_GREEN = "\033[38;5;46m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"


APP_NAME = "WEB SCRAPER PRO"
APP_VERSION = "v2.0"
FEATURE_COUNT = 18

# Full block-letter banner (pure ASCII, safe on every font)
BANNER_FULL = r"""
 __        __   _         ____                                  ____
 \ \      / /__| |__     / ___|  ___ _ __ __ _ _ __   ___ _ __  |  _ \ _ __ ___
  \ \ /\ / / _ \ '_ \    \___ \ / __| '__/ _` | '_ \ / _ \ '__| | |_) | '__/ _ \
   \ V  V /  __/ |_) |    ___) | (__| | | (_| | |_) |  __/ |    |  __/| | | (_) |
    \_/\_/ \___|_.__/    |____/ \___|_|  \__,_| .__/ \___|_|    |_|   |_|  \___/
                                               |_|
"""

BOOT_MODULES = [
    "core.config", "core.fetcher", "core.extractors",
    "core.crawler", "core.downloader", "core.exporter",
]


def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")


def term_width(default: int = 70) -> int:
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default


def hr(char: str = "=", color: str = C.GRAY):
    width = min(term_width(), 70)
    print(f"{color}{char * width}{C.RESET}")


# ------------------------------------------------------------------ #
# Boot checklist -- "[..] Loading module ... [OK]" hacker-tool style
# ------------------------------------------------------------------ #
def boot_checklist(animations: bool = True):
    clear_screen()
    print(f"{C.GRAY}{C.BOLD}[SYSTEM]{C.RESET} Initializing {APP_NAME} {APP_VERSION} ...\n")
    for mod in BOOT_MODULES:
        sys.stdout.write(f"  {C.GRAY}[..]{C.RESET} Loading {mod}")
        sys.stdout.flush()
        time.sleep(0.06 if animations else 0)
        sys.stdout.write(f"\r  {C.GREEN}[OK]{C.RESET} Loading {mod}\n")
        sys.stdout.flush()
    print(f"\n  {C.BRIGHT_GREEN}{C.BOLD}[READY]{C.RESET} All modules loaded -- {FEATURE_COUNT} features online.\n")
    time.sleep(0.3 if animations else 0)


# ------------------------------------------------------------------ #
# Matrix-rain intro -- ASCII-only (0/1) so it never breaks alignment
# on narrow / non-Unicode Termux fonts.
# ------------------------------------------------------------------ #
def matrix_intro(duration: float = 0.9, animations: bool = True):
    if not animations:
        return
    width = min(term_width(), 70)
    end_time = time.time() + duration
    try:
        while time.time() < end_time:
            line = "".join(
                f"{C.BRIGHT_GREEN}{random.choice('01')}{C.RESET}"
                if random.random() > 0.45 else " "
                for _ in range(width)
            )
            print(line)
            time.sleep(0.025)
    except KeyboardInterrupt:
        pass


# ------------------------------------------------------------------ #
# Typewriter effect
# ------------------------------------------------------------------ #
def typewriter(text: str, delay: float = 0.003, color: str = "", animations: bool = True):
    if not animations:
        print(f"{color}{text}{C.RESET}")
        return
    for ch in text:
        sys.stdout.write(f"{color}{ch}{C.RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    print()


# ------------------------------------------------------------------ #
# Boxed banner -- adapts to terminal width
# ------------------------------------------------------------------ #
def _boxed_line(text: str, width: int, color: str = C.WHITE) -> str:
    inner = width - 4
    text = text[:inner]
    pad = inner - len(text)
    left = pad // 2
    right = pad - left
    return f"{C.GRAY}|{C.RESET} {' ' * left}{color}{text}{C.RESET}{' ' * right} {C.GRAY}|{C.RESET}"


def draw_banner_box():
    width = max(40, min(term_width(), 78))
    print(f"{C.GRAY}{'+' + '-' * (width - 2) + '+'}{C.RESET}")
    print(_boxed_line(f"{APP_NAME} {APP_VERSION}", width, C.BRIGHT_GREEN + C.BOLD))
    print(_boxed_line("Advanced Modular Web Scraping Framework", width, C.CYAN))
    print(_boxed_line("Built for Termux  |  Pure Python  |  No Browser Needed", width, C.GRAY))
    print(_boxed_line(f"{FEATURE_COUNT} Features - crawler / extractor / analyzer / downloader", width, C.GRAY))
    print(f"{C.GRAY}{'+' + '-' * (width - 2) + '+'}{C.RESET}")


def show_full_banner():
    """Large block-letter banner for wide terminals."""
    print(f"{C.BRIGHT_GREEN}{C.BOLD}{BANNER_FULL}{C.RESET}")
    draw_banner_box()


def show_compact_banner():
    """Compact banner for narrow phone terminals."""
    draw_banner_box()


# ------------------------------------------------------------------ #
# Full boot sequence -- call this once at startup
# ------------------------------------------------------------------ #
def show_banner(animations: bool = True, boot: bool = True):
    if boot:
        boot_checklist(animations=animations)
        matrix_intro(duration=0.7, animations=animations)
    clear_screen()

    width = term_width()
    if width >= 80:
        show_full_banner()
    else:
        show_compact_banner()
    print()


# ------------------------------------------------------------------ #
# Loading spinner (used while a request is in-flight)
# ------------------------------------------------------------------ #
def spin(message: str, duration: float = 0.7, animations: bool = True):
    if not animations:
        print(f"{C.YELLOW}[~] {message}...{C.RESET}")
        return
    frames = ["|", "/", "-", "\\"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        frame = frames[i % len(frames)]
        sys.stdout.write(f"\r{C.CYAN}[{frame}] {message}...{C.RESET}")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")
    sys.stdout.flush()


# ------------------------------------------------------------------ #
# Progress bar (used for crawling / batch downloads)
# ------------------------------------------------------------------ #
def progress_bar(current: int, total: int, label: str = "", width: int = 30):
    if total <= 0:
        return
    filled = int(width * current / total)
    bar = "#" * filled + "-" * (width - filled)
    pct = int(100 * current / total)
    line = f"\r{C.GREEN}[{bar}] {pct:3d}% ({current}/{total}) {C.GRAY}{label[:40]}{C.RESET}"
    sys.stdout.write(line)
    sys.stdout.flush()
    if current >= total:
        print()


# ------------------------------------------------------------------ #
# Generic status printers
# ------------------------------------------------------------------ #
def ok(msg: str):
    print(f"{C.GREEN}[+] {msg}{C.RESET}")


def warn(msg: str):
    print(f"{C.YELLOW}[!] {msg}{C.RESET}")


def err(msg: str):
    print(f"{C.RED}[X] {msg}{C.RESET}")


def info(msg: str):
    print(f"{C.CYAN}[i] {msg}{C.RESET}")


def section(title: str):
    width = min(term_width(), 60)
    print(f"\n{C.MAGENTA}{C.BOLD}{'-' * width}{C.RESET}")
    print(f"{C.MAGENTA}{C.BOLD} {title}{C.RESET}")
    print(f"{C.MAGENTA}{C.BOLD}{'-' * width}{C.RESET}")


def ask(prompt: str, default: str = "") -> str:
    val = input(f"{C.CYAN}> {prompt}{C.RESET}").strip()
    return val if val else default
