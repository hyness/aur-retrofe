#!/usr/bin/env python3
"""Check GitHub for a newer RetroFE Release-X.Y.Z branch than what's pinned in PKGBUILD.

Prints GitHub Actions output variables: needs_update, new_version.
"""
import json
import os
import re
import sys
import urllib.request

REPO = "phulshof/RetroFE"
BRANCH_RE = re.compile(r"^Release-(\d+)\.(\d+)\.(\d+)$")


def current_version():
    with open("PKGBUILD") as f:
        text = f.read()
    return re.search(r'^pkgver=(\S+)$', text, re.M).group(1)


def _get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def latest_release_branch():
    best = None
    page = 1
    while True:
        branches = _get(f"https://api.github.com/repos/{REPO}/branches?per_page=100&page={page}")
        if not branches:
            break
        for b in branches:
            m = BRANCH_RE.match(b["name"])
            if not m:
                continue
            ver_tuple = tuple(int(x) for x in m.groups())
            ver_str = ".".join(m.groups())
            if best is None or ver_tuple > best[0]:
                best = (ver_tuple, ver_str)
        if len(branches) < 100:
            break
        page += 1
    return best[1] if best else None


def main():
    cur_ver = current_version()
    new_ver = latest_release_branch()
    if new_ver is None:
        print("Could not find any Release-X.Y.Z branch", file=sys.stderr)
        sys.exit(1)

    needs_update = new_ver != cur_ver

    gh_out = os.environ.get("GITHUB_OUTPUT")
    lines = [
        f"needs_update={'true' if needs_update else 'false'}",
        f"current_version={cur_ver}",
        f"new_version={new_ver}",
    ]
    print("\n".join(lines))
    if gh_out:
        with open(gh_out, "a") as f:
            f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
