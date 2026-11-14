#!/usr/bin/env python3
"""Fetch live stats and blog posts for the profile cards.

- Public GitHub stats (REST). Optional GraphQL (GITHUB_TOKEN or STATS_TOKEN)
  adds a total commit count. A PAT with read:user can include private commits
  via restrictedContributionsCount; GITHUB_TOKEN in Actions usually cannot.
- Latest posts from the kevinm.tech RSS feed.

Standard library only. Writes assets/profile.json.

    python3 scripts/fetch_profile_data.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

LOGIN = "kevinmedeiros"
FEED = "https://kevinm.tech/rss.xml"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "profile.json")
UA = "kevinmedeiros-profile-generator"
TOKEN = os.environ.get("STATS_TOKEN") or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")


def http_json(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, method="GET" if data is None else "POST")
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "application/vnd.github+json")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def rest_stats():
    user = http_json(f"https://api.github.com/users/{LOGIN}")
    stars, page, repos = 0, 1, 0
    while True:
        batch = http_json(
            f"https://api.github.com/users/{LOGIN}/repos?per_page=100&page={page}&type=owner"
        )
        if not batch:
            break
        for repo in batch:
            stars += repo.get("stargazerCount", repo.get("stargazers_count", 0))
            repos += 1
        if len(batch) < 100:
            break
        page += 1
    return {
        "repos": user.get("public_repos", repos),
        "stars": stars,
        "followers": user.get("followers", 0),
        "commits": None,
    }


def gql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    data = http_json(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )
    if "errors" in data:
        raise RuntimeError(json.dumps(data["errors"], indent=2))
    return data["data"]


def graphql_stats():
    user = gql(
        """query($login:String!){ user(login:$login){
             createdAt followers{totalCount}
             repositories(privacy:PUBLIC, ownerAffiliations:OWNER){totalCount}
           }}""",
        {"login": LOGIN},
    )["user"]
    stars, cursor = 0, None
    while True:
        page = gql(
            """query($login:String!,$cursor:String){ user(login:$login){
                 repositories(first:100, ownerAffiliations:OWNER, after:$cursor){
                   nodes{stargazerCount} pageInfo{hasNextPage endCursor}}}}""",
            {"login": LOGIN, "cursor": cursor},
        )["user"]["repositories"]
        stars += sum(n["stargazerCount"] for n in page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    commits = 0
    this_year = dt.datetime.now(dt.timezone.utc).year
    for year in range(int(user["createdAt"][:4]), this_year + 1):
        cc = gql(
            """query($login:String!,$from:DateTime!,$to:DateTime!){ user(login:$login){
                 contributionsCollection(from:$from,to:$to){
                   totalCommitContributions restrictedContributionsCount}}}""",
            {
                "login": LOGIN,
                "from": f"{year}-01-01T00:00:00Z",
                "to": f"{year}-12-31T23:59:59Z",
            },
        )["user"]["contributionsCollection"]
        commits += cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
    return {
        "repos": user["repositories"]["totalCount"],
        "stars": stars,
        "followers": user["followers"]["totalCount"],
        "commits": commits,
    }


def fetch_posts(limit=3):
    req = urllib.request.Request(FEED, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
    root = ET.fromstring(raw)
    items = []
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = (item.findtext("description") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        date_label = pub
        try:
            parsed = dt.datetime.strptime(pub, "%a, %d %b %Y %H:%M:%S %Z")
            date_label = parsed.strftime("%b %Y")
        except ValueError:
            try:
                parsed = dt.datetime.strptime(pub[:16], "%a, %d %b %Y")
                date_label = parsed.strftime("%b %Y")
            except ValueError:
                date_label = pub[:16] or ""
        if title and link:
            items.append(
                {"title": title, "url": link, "description": desc, "date": date_label}
            )
        if len(items) >= limit:
            break
    return items


def main():
    if TOKEN:
        try:
            stats = graphql_stats()
        except Exception as exc:
            print(f"GraphQL stats failed ({exc}); falling back to public REST.", file=sys.stderr)
            stats = rest_stats()
    else:
        stats = rest_stats()

    cfg_path = os.path.join(ROOT, "profile.config.json")
    limit = 3
    if os.path.exists(cfg_path):
        cfg = json.load(open(cfg_path))
        limit = int(cfg.get("posts", {}).get("count", 3))

    try:
        posts = fetch_posts(limit)
    except Exception as exc:
        print(f"RSS fetch failed ({exc}); keeping any existing posts.", file=sys.stderr)
        posts = []
        if os.path.exists(OUT):
            posts = json.load(open(OUT)).get("posts") or []

    payload = {**stats, "posts": posts, "updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    if os.path.exists(OUT):  # keep the old timestamp when nothing changed, so the daily run commits only real changes
        prev = json.load(open(OUT))
        if {k: v for k, v in prev.items() if k != "updated"} == {k: v for k, v in payload.items() if k != "updated"}:
            payload["updated"] = prev.get("updated", payload["updated"])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    print(f"Wrote {OUT}: repos={payload['repos']} stars={payload['stars']} "
          f"followers={payload['followers']} commits={payload['commits']} posts={len(posts)}")


if __name__ == "__main__":
    main()
