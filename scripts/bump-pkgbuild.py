#!/usr/bin/env python3
"""Bump PKGBUILD's pkgver to the given value and reset pkgrel.

No checksum to update: the source is a git checkout (md5sums=SKIP) and
the branch name interpolates $pkgver directly.
"""
import re
import sys


def main():
    new_ver = sys.argv[1]

    with open("PKGBUILD") as f:
        text = f.read()

    text = re.sub(r'^pkgver=\S+$', f'pkgver={new_ver}', text, count=1, flags=re.M)
    text = re.sub(r'^pkgrel=\S+$', 'pkgrel=1', text, count=1, flags=re.M)

    with open("PKGBUILD", "w") as f:
        f.write(text)


if __name__ == "__main__":
    main()
