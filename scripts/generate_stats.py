#!/usr/bin/env python3
"""Generates every graphic on the profile README from live GitHub data.

Pulls contribution/language data via the GitHub GraphQL API (through the
`gh` CLI, so it works identically whether run locally with a logged-in
`gh` session or in CI with GITHUB_TOKEN set) and renders it as plain SVG.
No third-party image services, no external fonts to embed - headings and
stats just use the viewer's own monospace font stack.

Run: python3 scripts/generate_stats.py
Env: GH_LOGIN (defaults to the authenticated gh user)
"""

import datetime
import json
import os
import subprocess
import sys

# ============================== Style ==============================

BG = "#0d1117"
CARD = "#161b22"
BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#2dd4bf"
FONT = "ui-monospace, 'JetBrains Mono', 'Fira Code', Consolas, monospace"

WIDTH = 620


def esc(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def text(x, y, s, size=13, weight="400", color=TEXT, anchor="start", spacing=None):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}"{ls}>{esc(s)}</text>'
    )


def svg(width, height, body, bg=BG):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        f'<rect width="{width}" height="{height}" rx="10" fill="{bg}" stroke="{BORDER}"/>'
        f"{body}</svg>"
    )


# ============================== GitHub API ==============================


def gh_graphql(query, **variables):
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        args += ["-f", f"{k}={v}"]
    out = subprocess.run(args, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)["data"]


def fetch_contributions(login):
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks { contributionDays { date contributionCount } }
          }
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
          totalRepositoriesWithContributedCommits
        }
      }
    }
    """
    return gh_graphql(query, login=login)["user"]["contributionsCollection"]


def fetch_languages(login):
    query = """
    query($login: String!) {
      user(login: $login) {
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
          nodes {
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges { size node { name color } }
            }
          }
        }
      }
    }
    """
    nodes = gh_graphql(query, login=login)["user"]["repositories"]["nodes"]
    by_bytes = {}
    by_repo_count = {}
    colors = {}
    for repo in nodes:
        seen_in_repo = set()
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            colors[name] = edge["node"]["color"] or MUTED
            by_bytes[name] = by_bytes.get(name, 0) + edge["size"]
            seen_in_repo.add(name)
        for name in seen_in_repo:
            by_repo_count[name] = by_repo_count.get(name, 0) + 1
    return by_bytes, by_repo_count, colors


# ============================== Streak math ==============================


def compute_streaks(days):
    """days: list of (date, count) ordered oldest -> newest."""
    today = datetime.date.today()
    counts = {d: c for d, c in days}

    longest = 0
    longest_end = None
    run = 0
    for d, c in days:
        if c > 0:
            run += 1
            if run > longest:
                longest = run
                longest_end = d
        else:
            run = 0
    longest_start = None
    if longest_end:
        longest_start = longest_end - datetime.timedelta(days=longest - 1)

    current = 0
    cursor = today
    # today may not have a contribution yet; don't break the streak on it alone
    if counts.get(today, 0) == 0:
        cursor = today - datetime.timedelta(days=1)
    while counts.get(cursor, 0) > 0:
        current += 1
        cursor -= datetime.timedelta(days=1)
    current_end = today if counts.get(today, 0) > 0 else (cursor + datetime.timedelta(days=1))
    current_start = current_end - datetime.timedelta(days=current - 1) if current else None

    return {
        "current": current,
        "current_range": (current_start, current_end) if current else None,
        "longest": longest,
        "longest_range": (longest_start, longest_end) if longest else None,
    }


# ============================== Renderers ==============================


def render_heading(label):
    """A section heading, e.g. hd-about.svg -- plain styled text, no embedded font."""
    height = 40
    body = text(0, 27, label.upper(), size=15, weight="700", color=ACCENT, spacing="0.12em")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}">{body}'
        f'<line x1="0" y1="36" x2="{WIDTH}" y2="36" stroke="{BORDER}" stroke-width="1"/></svg>'
    )


def render_stats(cc):
    cal = cc["contributionCalendar"]
    total = cal["totalContributions"]
    height = 110
    parts = [text(24, 44, f"{total:,}", size=32, weight="700", color=TEXT)]
    parts.append(text(24, 66, "contributions in the last year", size=13, color=MUTED))

    stats = [
        ("commits", cc["totalCommitContributions"]),
        ("pull requests", cc["totalPullRequestContributions"]),
        ("issues", cc["totalIssueContributions"]),
        ("reviews", cc["totalPullRequestReviewContributions"]),
        ("repos touched", cc["totalRepositoriesWithContributedCommits"]),
    ]
    col_w = (WIDTH - 48) / len(stats)
    for i, (label, value) in enumerate(stats):
        x = 24 + i * col_w
        parts.append(text(x, 90, f"{value:,}", size=16, weight="700", color=ACCENT))
        parts.append(text(x, 104, label, size=10, color=MUTED))

    return svg(WIDTH, height, "".join(parts))


def fmt_day(d):
    return f"{d.strftime('%b')} {d.day}"


def fmt_range(r):
    if not r:
        return "-"
    start, end = r
    if start == end:
        return fmt_day(start)
    return f"{fmt_day(start)} - {fmt_day(end)}"


def render_streak(streaks):
    height = 90
    halves = [
        ("current streak", streaks["current"], streaks["current_range"]),
        ("longest streak", streaks["longest"], streaks["longest_range"]),
    ]
    parts = []
    col_w = WIDTH / 2
    for i, (label, value, rng) in enumerate(halves):
        x = 24 + i * col_w
        parts.append(text(x, 40, f"{value}", size=30, weight="700", color=ACCENT if i == 0 else TEXT))
        parts.append(text(x + 46, 40, "days", size=12, color=MUTED))
        parts.append(text(x, 60, label, size=12, color=MUTED))
        parts.append(text(x, 78, fmt_range(rng), size=11, color=MUTED))
    parts.append(f'<line x1="{WIDTH/2}" y1="16" x2="{WIDTH/2}" y2="74" stroke="{BORDER}"/>')
    return svg(WIDTH, height, "".join(parts))


def render_langs(by_bytes, by_repo_count, colors):
    top_bytes = sorted(by_bytes.items(), key=lambda kv: -kv[1])[:6]
    top_repos = sorted(by_repo_count.items(), key=lambda kv: -kv[1])[:6]
    total_bytes = sum(by_bytes.values()) or 1

    height = 40 + 24 * max(len(top_bytes), len(top_repos)) + 20
    parts = [
        text(24, 30, "by bytes", size=11, color=MUTED, weight="700", spacing="0.08em"),
        text(WIDTH / 2 + 12, 30, "by repo count", size=11, color=MUTED, weight="700", spacing="0.08em"),
    ]

    bar_w = WIDTH / 2 - 60
    for i, (name, size) in enumerate(top_bytes):
        y = 54 + i * 24
        pct = size / total_bytes
        color = colors.get(name, MUTED)
        parts.append(f'<rect x="24" y="{y-11}" width="{bar_w}" height="6" rx="3" fill="{BORDER}"/>')
        parts.append(f'<rect x="24" y="{y-11}" width="{max(bar_w*pct,3):.1f}" height="6" rx="3" fill="{color}"/>')
        parts.append(text(24, y + 8, f"{name} - {pct*100:.0f}%", size=11, color=TEXT))

    for i, (name, count) in enumerate(top_repos):
        y = 54 + i * 24
        color = colors.get(name, MUTED)
        x0 = WIDTH / 2 + 12
        parts.append(f'<circle cx="{x0+4}" cy="{y+4}" r="4" fill="{color}"/>')
        parts.append(text(x0 + 14, y + 8, f"{name} - {count} repo{'s' if count != 1 else ''}", size=11, color=TEXT))

    return svg(WIDTH, height, "".join(parts))


# ============================== Main ==============================


def main():
    login = os.environ.get("GH_LOGIN")
    if not login:
        login = subprocess.run(
            ["gh", "api", "user", "--jq", ".login"], capture_output=True, text=True, check=True
        ).stdout.strip()

    cc = fetch_contributions(login)
    by_bytes, by_repo_count, colors = fetch_languages(login)

    days = []
    for week in cc["contributionCalendar"]["weeks"]:
        for day in week["contributionDays"]:
            d = datetime.date.fromisoformat(day["date"])
            days.append((d, day["contributionCount"]))
    days.sort()

    streaks = compute_streaks(days)

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def write(name, content):
        with open(os.path.join(root, name), "w", encoding="utf-8") as f:
            f.write(content)

    write("stats.svg", render_stats(cc))
    write("streak.svg", render_streak(streaks))
    write("langs.svg", render_langs(by_bytes, by_repo_count, colors))

    for slug, label in [
        ("about", "about"),
        ("stack", "stack"),
        ("projects", "projects"),
        ("stats", "stats"),
        ("about-this-page", "about this page"),
    ]:
        write(f"hd-{slug}.svg", render_heading(label))

    print(f"Generated stats for {login}: "
          f"{cc['contributionCalendar']['totalContributions']} contributions, "
          f"current streak {streaks['current']}, longest {streaks['longest']}.")


if __name__ == "__main__":
    sys.exit(main())
