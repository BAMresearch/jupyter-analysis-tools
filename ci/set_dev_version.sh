#!/bin/bash

ver="$(tbump current-version)"
newver="${ver%.*}.$((${ver##*.}+1))"
commits_since_release="$(git log v$ver..HEAD --oneline | wc -l)"
commit_short="$(git rev-parse --short HEAD)"
#devver="$(printf "%s.dev%d+%s\n" "$newver" "$commits_since_release" "$commit_short")"
devver="$(printf "%s.dev%d\n" "$newver" "$commits_since_release")"
tbump --only-patch --non-interactive "$devver"
