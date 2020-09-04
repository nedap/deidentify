#!/bin/bash
set -e

if [[ $# -eq 0 ]] ; then
    echo 'usage: ./release.sh <version>'
    echo 'example: ./release.sh 0.3.2'
    exit 1
fi

version=$1
export RELEASE_VERSION=$version

read -rsp "Enter GitHub access token for Changelog generation: " github_token
echo
echo "Release version: $version"
sed -i '' "s/^__version__ .*/__version__ = \"$version\"/g" deidentify/__init__.py

# Create new tag
git commit -a -m "Bump version to $version"
git tag -a "v$version" -m "v$version"
git push --follow-tags

make publish

github_changelog_generator --exclude-tags-regex "^model.*" -u nedap -p deidentify -t "$github_token"
git add CHANGELOG.md
git commit -m "Update CHANGELOG.md"
git push

echo "Please create a new release and add the contents of the corresponding changelog section."
echo "Visit: https://github.com/nedap/deidentify/releases/edit/v$version"
