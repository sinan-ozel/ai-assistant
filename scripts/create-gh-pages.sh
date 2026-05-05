#!/usr/bin/env bash
set -e

git checkout --orphan gh-pages
git reset --hard
git commit --allow-empty -m "Initialize gh-pages"
git push origin gh-pages
git checkout -
echo "gh-pages branch created and pushed."
