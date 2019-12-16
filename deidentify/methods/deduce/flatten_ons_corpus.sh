#!/bin/bash
# Convert fine-grained location types to a broader "Named_Location" type.
#
# Usage:
# ./flatten_ons_corpus.sh <corpus_name>
#
# Example:
# ./flatten_ons_corpus.sh ons

corpus_name=$1
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
corpus_dir=$DIR/../../../data/corpus/$corpus_name
corpus_flattened_dir=$DIR/../../../data/corpus/"$corpus_name-flattened"

if [ -d "$corpus_flattened_dir" ]; then
  echo "A flattend corpus already exists in $corpus_flattened_dir"
  exit 1
fi

replacements=( "Hospital:Named_Location"
        "Care_Institute:Named_Location"
        "Organization_Company:Named_Location"
        "Internal_Location:Named_Location"
        "Email:URL_IP" )

echo "Create flattened corpus in $corpus_flattened_dir"
cp -r "$corpus_dir" "$corpus_flattened_dir"

for pair in "${replacements[@]}" ; do
  original="${pair%%:*}"
  replacement="${pair##*:}"

  echo "$original -> $replacement"

  find "$corpus_flattened_dir" -type f -name '*.ann' -exec sed -i -e "s/^\(T[0-9]*.*\)$original/\1$replacement/" {} \;
done
