"""Takes all *.txt/*.ann files within a directory and creates a corpus in the form of:

```
data/corpus/{corpus_name}/
├── dev
│   ├── doc_0002.ann
│   └── doc_0002.txt
├── test
│   ├── doc_0003.ann
│   └── doc_0003.txt
└── train
    ├── doc_0001.ann
    └── doc_0001.txt
```

Train/dev/test split is done in a 60/20/20 ratio.
"""
import argparse
import glob
import os
import random
import shutil
from os.path import abspath, basename, dirname, join, splitext

from loguru import logger

DATA_PATH = join(abspath(dirname(__file__)), '../../data/corpus')


def main(args):
    filenames = glob.glob(join(args.data_path, '*.ann'))
    filenames = sorted(filenames)
    random.seed(42)
    random.shuffle(filenames)

    split_1 = int(0.6 * len(filenames))
    split_2 = int(0.8 * len(filenames))
    train = filenames[:split_1]
    dev = filenames[split_1:split_2]
    test = filenames[split_2:]

    logger.info('Number of train/dev/test files: {}/{}/{}'.format(len(train), len(dev), len(test)))
    logger.info('Write corpus "{}" to "{}"'.format(args.corpus_name, DATA_PATH))

    i = 1
    for part_name, ann_files in zip(['train', 'dev', 'test'], [train, dev, test]):
        part_path = join(DATA_PATH, args.corpus_name, part_name)
        os.makedirs(part_path)

        for ann_file in ann_files:
            txt_file = '{}.txt'.format(splitext(ann_file)[0])

            if args.rename_files:
                shutil.copy2(ann_file, join(part_path, 'doc_{:04d}.ann'.format(i)))
                shutil.copy2(txt_file, join(part_path, 'doc_{:04d}.txt'.format(i)))
            else:
                shutil.copy2(ann_file, join(part_path, basename(ann_file)))
                shutil.copy2(txt_file, join(part_path, basename(txt_file)))
            i += 1

    logger.info('Done.')


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.set_defaults(feature=True)
    parser.add_argument("corpus_name", help="Name of the corpus")
    parser.add_argument("data_path",
                        help="Directory of text files in standoff format (e.g., .txt/.ann pairs)")
    parser.add_argument('--rename_files',
                        dest='rename_files',
                        action='store_true',
                        help="If this option is passed, files are renamed to: `doc_{i}.{txt,ann}`")
    parser.set_defaults(rename_files=False)
    return parser.parse_args()


if __name__ == '__main__':
    main(arg_parser())
