"""Download a model archive from a GitHub release (tagged `tag`) to the local model cache.

Assumes that the release has an asset with name `{tag}.tar.gz`. The archive is extracted in the
model cache directory.

Usage info:
python -m deidentify.util.download_model --help
"""
import argparse
import os
import re
import shutil
import sys
import tarfile
import tempfile
from os.path import exists, join

import requests
from loguru import logger
from tqdm import tqdm

import deidentify


def download_file(url: str, cache_dir: str):
    os.makedirs(cache_dir, exist_ok=True)

    archive_basename = re.sub(r".+/", "", url)
    target_name = archive_basename.split('.tar.gz')[0]
    cache_archive_path = join(cache_dir, archive_basename)
    cache_target_path = join(cache_dir, target_name)

    if exists(cache_target_path):
        logger.info('Skip download. File already exists at: {}', cache_target_path)
        sys.exit()

    fd, temp_filename = tempfile.mkstemp()
    try:
        logger.info("Could not find file in cache. Download {} to {}", url, temp_filename)

        req = requests.get(url, stream=True)
        content_length = req.headers.get("Content-Length")
        total = int(content_length) if content_length is not None else None
        progress = tqdm(unit="B", total=total, unit_scale=True, unit_divisor=1024)
        with os.fdopen(fd, 'wb') as temp_file:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    progress.update(len(chunk))
                    temp_file.write(chunk)

        progress.close()

        logger.info("Copy temporary file {} to cache at {}", temp_filename, cache_archive_path)
        shutil.copyfile(temp_filename, cache_archive_path)
    finally:
        os.remove(temp_filename)

    logger.info("Extracting {}", cache_archive_path)
    with tarfile.open(cache_archive_path, "r:gz") as tar:
        tar.extractall(cache_dir)
    os.remove(cache_archive_path)


def main(args):
    url = (
        f'https://github.com/{args.owner}/{args.repo}/releases/download/{args.tag}/'
        f'{args.tag}.tar.gz'
    )
    download_file(url, args.cache_dir)


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('tag', help='Release tag.')
    parser.add_argument('--cache_dir',
                        help='Local directory to store models. Default: %(default)s.',
                        default=deidentify.cache_root)
    parser.add_argument('--owner',
                        help='Name of GitHub user or organization. Default: %(default)s.',
                        default='nedap')
    parser.add_argument('--repo',
                        help='Name of GitHub repo of "owner". Default: %(default)s.',
                        default='deidentify')
    return parser.parse_args()


if __name__ == '__main__':
    main(arg_parser())
