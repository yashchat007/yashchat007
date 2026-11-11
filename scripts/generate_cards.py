#!/usr/bin/env python3
"""Generate original profile cards for yashchat007.

Layout inspired by AVIVASHISHTA29's card stack. Palette is ink + electric blue.
The LeetCode heatmap is built from LeetCode's public GraphQL calendar
(userProfileCalendar / submissionCalendar) so the README can show a live
grid without Easy/Medium/Hard charts. A daily GitHub Action regenerates
cards/heatmap.svg. Do not invent cells — if the fetch fails, skip the grid.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "cards"
FONT_DIRS = [ROOT / "assets" / "fonts", Path("/tmp/yash-assets")]

# Ink + electric blue, with Avi-like light neutrals. No red/orange.
PAPER = "#F3F3F1"
INK = "#111111"
MUTED = "#6E6E73"
SOFT = "#3A3A3C"
ACCENT = "#2F55FF"
WHITE = "#FFFFFF"

# Heatmap only. Grey is reserved for zero-submission days. Any day with
# at least one submission uses a saturated, clearly visible blue.
HEAT_EMPTY = "#E5E5E3"
HEAT_BLUES = ("#7B95FF", "#5474FF", "#2F55FF", "#1A36C8")

W = 880.0
GAP = 8.0
BOTTOM = 12.0

LEETCODE_USERNAME = os.environ.get("LEETCODE_USERNAME", "Oru388f3ta")
LEETCODE_GRAPHQL = "https://leetcode.com/graphql"

PORTFOLIO = "yash-chaturvedi-portfolio.vercel.app"

CALENDAR_QUERY = """
query userProfileCalendar($username: String!, $year: Int) {
  matchedUser(username: $username) {
    userCalendar(year: $year) {
      activeYears
      streak
      totalActiveDays
      submissionCalendar
    }
  }
}
""".strip()


def find_font(name: str) -> Path:
    for folder in FONT_DIRS:
        path = folder / name
        if path.exists():
            return path
    raise FileNotFoundError(f"Font not found: {name} (looked in {FONT_DIRS})")


def b64_font(name: str) -> str:
    return base64.b64encode(find_font(name).read_bytes()).decode("ascii")


FONT_CSS = f"""
@font-face {{
  font-family: 'Instrument Serif';
  font-style: normal;
  font-weight: 400;
  src: url('data:font/woff2;base64,{b64_font('instrument-serif.woff2')}') format('woff2');
}}
@font-face {{
  font-family: 'Instrument Serif';
  font-style: italic;
  font-weight: 400;
  src: url('data:font/woff2;base64,{b64_font('instrument-serif-italic.woff2')}') format('woff2');
}}
@font-face {{
  font-family: 'Instrument Sans';
  font-style: normal;
  font-weight: 400;
  src: url('data:font/woff2;base64,{b64_font('instrument-sans.woff2')}') format('woff2');
}}
@font-face {{
  font-family: 'DM Mono';
  font-style: normal;
  font-weight: 400;
  src: url('data:font/woff2;base64,{b64_font('dm-mono.woff2')}') format('woff2');
}}
@font-face {{
  font-family: 'DM Mono';
  font-style: normal;
  font-weight: 500;
  src: url('data:font/woff2;base64,{b64_font('dm-mono-medium.woff2')}') format('woff2');
}}
""".strip()

SERIF = "'Instrument Serif', Georgia, serif"
SANS = "'Instrument Sans', system-ui, -apple-system, sans-serif"
MONO = "'DM Mono', ui-monospace, SFMono-Regular, Menlo, monospace"


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def svg_wrap(width: float, height: float, body: str, label: str, extra_style: str = "") -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width:.3f}" height="{height:.3f}" viewBox="0 0 {width:.3f} {height:.3f}" role="img" aria-label="{esc(label)}">
<title>{esc(label)}</title>
<defs>
<style>
{FONT_CSS}
{extra_style}
</style>
</defs>
{body}
</svg>
'''


def write(name: str, content: str) -> None:
    path = CARDS / name
    path.write_text(content)
    print(f"wrote {path} ({path.stat().st_size} bytes)")


def hero() -> None:
    width, height = W, 436.0
    card_h = height - BOTTOM
    # Typographic only. CSE appears once, as a quiet footer line.
    # Exactly one short DRDO line; no other workplace or internship details.
    body = f'''
<rect width="{W}" height="{card_h}" rx="14" fill="{PAPER}"/>
<rect x="48" y="44" width="8" height="8" rx="2" fill="{ACCENT}"/>
<text x="66" y="53" font-family="{MONO}" font-size="12" letter-spacing="1.1" fill="{MUTED}">COMPETITIVE PROGRAMMER · BUILDER</text>
<text x="44" y="176" font-family="{SERIF}" font-size="120" letter-spacing="-2.5" fill="{INK}">Yash</text>
<text x="44" y="278" font-family="{SERIF}" font-style="italic" font-size="100" letter-spacing="-2.2" fill="{INK}">Chatur<tspan fill="{ACCENT}">vedi</tspan></text>
<text x="48" y="328" font-family="{SANS}" font-size="18" fill="{SOFT}">I love working on complex software problems.</text>
<text x="48" y="354" font-family="{SANS}" font-size="16" fill="{MUTED}">Former intern @ DRDO HQ</text>
<text x="48" y="382" font-family="{MONO}" font-size="12" fill="{MUTED}">CSE, Manipal University Jaipur</text>
<text x="48" y="406" font-family="{MONO}" font-size="12" fill="{INK}">{esc(PORTFOLIO)}</text>
<g transform="translate(338 397)" fill="none" stroke="{ACCENT}" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">
  <path d="M0 8 L8 0 M8 0 H2.5 M8 0 V5.5"/>
</g>
'''
    write(
        "hero.svg",
        svg_wrap(
            width,
            height,
            body,
            "Yash Chaturvedi. I love working on complex software problems. Former intern @ DRDO HQ.",
        ),
    )


def stat_card(filename: str, label: str, number: str, lines: list[str], fill: str, ink: str, aria: str) -> None:
    width, height = 293.333, 222.0
    cw, ch = width - GAP, height - BOTTOM
    line_xml = []
    y = 148
    for line in lines:
        line_xml.append(
            f'<text x="22" y="{y}" font-family="{SANS}" font-size="13.5" fill="{ink}" opacity="0.92">{esc(line)}</text>'
        )
        y += 20
    body = f'''
<rect width="{cw}" height="{ch}" rx="14" fill="{fill}"/>
<text x="22" y="38" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{ink}">{esc(label)}</text>
<text x="252" y="38" font-family="{MONO}" font-size="14" fill="{ink}">→</text>
<text x="22" y="112" font-family="{SERIF}" font-size="44" fill="{ink}">{esc(number)}</text>
{''.join(line_xml)}
'''
    write(filename, svg_wrap(width, height, body, aria))


def repo_card(filename: str, name: str, lines: list[str], meta: str, label: str, width: float = 293.333) -> None:
    height = 188.0
    cw, ch = width - GAP, height - BOTTOM
    desc = []
    y = 72
    for line in lines:
        desc.append(
            f'<text x="24" y="{y}" font-family="{SANS}" font-size="14" fill="{SOFT}">{esc(line)}</text>'
        )
        y += 21
    body = f'''
<rect width="{cw}" height="{ch}" rx="14" fill="{PAPER}"/>
<rect x="24" y="30" width="8" height="8" rx="2" fill="{ACCENT}"/>
<text x="40" y="39" font-family="{SANS}" font-weight="500" font-size="18" fill="{INK}">{esc(name)}</text>
{''.join(desc)}
<text x="24" y="152" font-family="{MONO}" font-size="12" fill="{MUTED}">{esc(meta)}</text>
'''
    write(filename, svg_wrap(width, height, body, label))


def title_card(filename: str, before: str, italic: str, fill: str, label: str) -> None:
    width, height = W, 64.0
    body = f'''
<text x="2" y="46" font-family="{SERIF}" font-size="34" fill="{fill}">{esc(before)}<tspan font-style="italic">{esc(italic)}</tspan></text>
'''
    write(filename, svg_wrap(width, height, body, label))


def level_color(level: int) -> str:
    """Map a submission intensity level (0–4) to the heatmap scale."""
    if level <= 0:
        return HEAT_EMPTY
    return HEAT_BLUES[max(0, min(level, len(HEAT_BLUES)) - 1)]


def quartile_bounds(values: list[int]) -> tuple[int, int, int]:
    """Upper counts for heatmap levels 1–3; level 4 is anything above Q3.

    Bounds are quartiles of non-zero days in the visible window so the
    four blue levels are spread evenly instead of collapsing on low counts.
    """
    xs = sorted(int(v) for v in values)
    if not xs:
        return (1, 2, 3)
    n = len(xs)

    def at(q: int) -> int:
        # q is 1, 2, or 3. Use the upper item of that quartile.
        i = min(n - 1, max(0, (q * n) // 4 - 1 if (q * n) % 4 == 0 else (q * n) // 4))
        return xs[i]

    return at(1), at(2), at(3)


def count_to_level(count: int, bounds: tuple[int, int, int]) -> int:
    if count <= 0:
        return 0
    q1, q2, q3 = bounds
    if count <= q1:
        return 1
    if count <= q2:
        return 2
    if count <= q3:
        return 3
    return 4


def sunday_on_or_before(day: date) -> date:
    return day - timedelta(days=(day.weekday() + 1) % 7)


def leetcode_graphql(username: str, year: int | None = None) -> dict:
    variables: dict = {"username": username}
    if year is not None:
        variables["year"] = year
    req = urllib.request.Request(
        LEETCODE_GRAPHQL,
        data=json.dumps({"query": CALENDAR_QUERY, "variables": variables}).encode(),
        headers={
            "Content-Type": "application/json",
            "Referer": f"https://leetcode.com/{username}/",
            "Origin": "https://leetcode.com",
            "User-Agent": "Mozilla/5.0 (compatible; yashchat007-profile-heatmap/1.0)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = resp.read()
            status = resp.status
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"LeetCode GraphQL HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"LeetCode GraphQL request failed: {exc.reason}") from exc
    if status != 200:
        raise RuntimeError(f"LeetCode GraphQL HTTP {status}")
    payload = json.loads(body.decode())
    if payload.get("errors"):
        raise RuntimeError(f"LeetCode GraphQL errors: {payload['errors']}")
    user = (payload.get("data") or {}).get("matchedUser")
    if not user:
        raise RuntimeError(f"LeetCode user not found: {username}")
    return user.get("userCalendar") or {}


def parse_submission_calendar(raw) -> dict[date, int]:
    if isinstance(raw, str):
        raw = json.loads(raw)
    if not isinstance(raw, dict):
        return {}
    counts: dict[date, int] = {}
    for ts, n in raw.items():
        day = datetime.fromtimestamp(int(ts), tz=timezone.utc).date()
        counts[day] = counts.get(day, 0) + int(n)
    return counts


def fetch_heatmap_counts(username: str) -> tuple[dict[date, int], date, date]:
    today = datetime.now(timezone.utc).date()
    start = sunday_on_or_before(today) - timedelta(weeks=52)
    end = start + timedelta(days=53 * 7)  # exclusive; full 53×7 grid

    probe = leetcode_graphql(username, year=today.year)
    years = set(probe.get("activeYears") or [])
    years.add(start.year)
    years.add(today.year)
    years = {int(y) for y in years if start.year <= int(y) <= today.year}

    counts: dict[date, int] = {}
    for year in sorted(years):
        calendar = probe if year == today.year else leetcode_graphql(username, year=year)
        for day, n in parse_submission_calendar(calendar.get("submissionCalendar")).items():
            counts[day] = n

    filled = sum(1 for d, n in counts.items() if start <= d < end and n > 0)
    print(
        f"heatmap graphql user={username} years={sorted(years)} "
        f"active_in_window={filled} total_days_logged={len(counts)} "
        f"{start.isoformat()}–{(end - timedelta(days=1)).isoformat()}"
    )
    if filled < 30:
        raise RuntimeError(f"Unexpected heatmap activity count: {filled}")
    return counts, start, end


def heatmap() -> bool:
    try:
        counts, start, end = fetch_heatmap_counts(LEETCODE_USERNAME)
    except Exception as exc:
        print("WARNING: could not build live heatmap:", exc, file=sys.stderr)
        return False

    width, height = W, 268.0
    card_h = height - BOTTOM
    grid_x, grid_y = 40.0, 108.0
    grid_w, grid_h = 800.0, 112.0
    n_weeks, n_days = 53, 7
    gap = 2.4
    cell = min((grid_w - gap * (n_weeks - 1)) / n_weeks, (grid_h - gap * (n_days - 1)) / n_days)

    window_counts = [counts.get(start + timedelta(days=i), 0) for i in range((end - start).days)]
    nonzero = [c for c in window_counts if c > 0]
    bounds = quartile_bounds(nonzero)
    print(
        f"heatmap buckets Q1={bounds[0]} Q2={bounds[1]} Q3={bounds[2]} "
        f"(level 1: 1–{bounds[0]}, 2: {bounds[0]+1}–{bounds[1]}, "
        f"3: {bounds[1]+1}–{bounds[2]}, 4: {bounds[2]+1}+; "
        f"colors empty={HEAT_EMPTY} blues={list(HEAT_BLUES)})"
    )

    rects = []
    levels = []
    day = start
    week = 0
    while day < end:
        dow = (day.weekday() + 1) % 7  # Sunday = 0
        level = count_to_level(counts.get(day, 0), bounds)
        levels.append(level)
        px = grid_x + week * (cell + gap)
        py = grid_y + dow * (cell + gap)
        rects.append(
            f'<rect x="{px:.2f}" y="{py:.2f}" width="{cell:.2f}" height="{cell:.2f}" rx="2" fill="{level_color(level)}"/>'
        )
        day += timedelta(days=1)
        if (day.weekday() + 1) % 7 == 0:
            week += 1

    print(f"heatmap cells={len(rects)} levels={Counter(levels)}")

    legend = []
    lx = 40.0
    ly = 236.0
    legend.append(
        f'<text x="{lx}" y="{ly+8}" font-family="{MONO}" font-size="11" fill="{MUTED}">less</text>'
    )
    swatches = [HEAT_EMPTY, *HEAT_BLUES]
    sx = lx + 40
    for i, col in enumerate(swatches):
        legend.append(
            f'<rect x="{sx + i*14:.1f}" y="{ly-2}" width="11" height="11" rx="2" fill="{col}"/>'
        )
    legend.append(
        f'<text x="{sx + len(swatches)*14 + 8:.1f}" y="{ly+8}" font-family="{MONO}" font-size="11" fill="{MUTED}">more</text>'
    )

    body = f'''
<rect width="{W}" height="{card_h}" rx="14" fill="{PAPER}"/>
<text x="40" y="40" font-family="{MONO}" font-size="12" letter-spacing="1.1" fill="{MUTED}">LEETCODE · LAST 52 WEEKS</text>
<text x="40" y="84" font-family="{SERIF}" font-size="36" fill="{INK}">Submission grid</text>
{''.join(rects)}
{''.join(legend)}
'''
    write(
        "heatmap.svg",
        svg_wrap(
            width,
            height,
            body,
            "LeetCode submission grid for the last 52 weeks.",
        ),
    )
    return True


def highlights_card() -> None:
    """Full-width highlights panel from the portfolio — no workplace copy, no repeated stat-card numbers."""
    width, height = W, 226.0
    card_h = height - BOTTOM
    body = f'''
<rect width="{W}" height="{card_h}" rx="14" fill="{PAPER}"/>
<rect x="40" y="34" width="8" height="8" rx="2" fill="{ACCENT}"/>
<text x="58" y="43" font-family="{MONO}" font-size="12" letter-spacing="1.2" fill="{MUTED}">HIGHLIGHTS</text>
<text x="40" y="100" font-family="{SERIF}" font-size="36" fill="{INK}"><tspan fill="{ACCENT}">2,000+</tspan> problems across three platforms.</text>
<text x="40" y="146" font-family="{SANS}" font-size="16" fill="{SOFT}">Best LeetCode contest rank 1,633 of 30,000+.</text>
<text x="40" y="174" font-family="{SANS}" font-size="16" fill="{SOFT}">134 problems on Codeforces in a month.</text>
<text x="40" y="202" font-family="{SANS}" font-size="16" fill="{SOFT}">Listed in the takeUforward Hall of Fame.</text>
'''
    write(
        "highlights.svg",
        svg_wrap(
            width,
            height,
            body,
            "Highlights: 2,000+ problems across three platforms; best LeetCode contest rank 1,633 of 30,000+; 134 problems on Codeforces in a month; takeUforward Hall of Fame.",
        ),
    )


def generate_static_cards() -> None:
    hero()
    stat_card(
        "stat-leetcode.svg",
        "LEETCODE",
        "1,863",
        ["Knight · top 6.01%.", "962 problems solved."],
        ACCENT,
        WHITE,
        "LeetCode Knight, contest rating 1,863, top 6.01%, 962 problems solved.",
    )
    stat_card(
        "stat-codeforces.svg",
        "CODEFORCES",
        "1,287",
        ["Pupil.", "Current contest rating."],
        INK,
        WHITE,
        "Codeforces Pupil, rating 1,287.",
    )
    stat_card(
        "stat-tuf.svg",
        "TUF",
        "2,802",
        ["Contributions in the last 12 months.", "309 active days, 220-day best streak."],
        PAPER,
        INK,
        "takeUforward: 2,802 contributions in the last 12 months, 309 active days, 220-day best streak.",
    )
    title_card("title-building-light.svg", "What I'm ", "building", INK, "What I'm building")
    title_card("title-building-dark.svg", "What I'm ", "building", PAPER, "What I'm building")
    title_card("title-board-light.svg", "On the ", "board", INK, "On the board")
    title_card("title-board-dark.svg", "On the ", "board", PAPER, "On the board")

    highlights_card()

    # Six public projects in two even rows of three. The only remaining public
    # repos are Jarvis (2020 voice demo) and Yash_portfolio (already in the hero).
    repo_card(
        "repo-graphite.svg",
        "Graphite",
        ["Task dashboard with a focus", "stopwatch and cross-device", "sync."],
        "TypeScript  ·  Live",
        "Graphite: task dashboard with a focus stopwatch and cross-device sync.",
    )
    repo_card(
        "repo-roleradar.svg",
        "RoleRadar",
        ["Discovers India-eligible roles", "from 8 career sites, ranked on", "four explained dimensions."],
        "Python",
        "RoleRadar: job discovery across 8 company career sites, with four-dimension matching that explains the fit.",
    )
    repo_card(
        "repo-friday.svg",
        "FRIDAY",
        ["Local Windows desktop agent,", "with Ollama and Playwright.", "Every action is confirmed first."],
        "TypeScript",
        "FRIDAY: local Windows desktop agent with Ollama and Playwright. Actions are proposed and confirmed before they run.",
    )
    repo_card(
        "repo-gesture.svg",
        "Gesture Control",
        ["Hands-free Windows control from", "a webcam. Pinch-to-click and drag,", "calibrated per person."],
        "Python",
        "Gesture Control: hands-free Windows control from a webcam, with pinch-to-click and drag calibrated per person.",
    )
    repo_card(
        "repo-constellation.svg",
        "Constellation",
        ["Desktop lyrics visualizer that", "follows whatever is playing, with", "a constellation display."],
        "TypeScript",
        "Constellation: desktop lyrics visualizer that follows whatever is playing.",
    )
    repo_card(
        "repo-cinecircle.svg",
        "CineCircle",
        ["Watchlists, ratings, reviews,", "follows, and genre-based recs.", "Spring Boot + React."],
        "Java  ·  Live",
        "CineCircle: social movie platform with watchlists, ratings, reviews, follows, and genre-based recommendations (Spring Boot + React).",
    )
    for stale in (
        "now.svg",
        "repo-notes.svg",
        "stat-rating.svg",
        "stat-solved.svg",
        "stat-streak.svg",
    ):
        stale_path = CARDS / stale
        if stale_path.exists():
            stale_path.unlink()
            print("removed", stale_path)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate GitHub profile cards.")
    parser.add_argument(
        "--heatmap-only",
        action="store_true",
        help="Regenerate only cards/heatmap.svg from LeetCode's public GraphQL API.",
    )
    args = parser.parse_args(argv)
    CARDS.mkdir(parents=True, exist_ok=True)
    if args.heatmap_only:
        ok = heatmap()
        if not ok:
            sys.exit(1)
        return
    generate_static_cards()
    ok = heatmap()
    print("heatmap_ok", ok)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
