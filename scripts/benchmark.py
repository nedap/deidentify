import argparse
from timeit import default_timer as timer
from typing import List

import numpy as np
import pandas as pd
from flair.datasets import CONLL_03_DUTCH
from loguru import logger
from tqdm import tqdm

from deidentify.base import Document
from deidentify.taggers import CRFTagger, DeduceTagger, FlairTagger, TextTagger
from deidentify.tokenizer import TokenizerFactory

N_REPETITIONS = 5
N_SENTS = 5000


def load_data():
    corpus = CONLL_03_DUTCH()
    sentences = corpus.train[:N_SENTS]
    tokens = sum(len(sent) for sent in sentences)
    docs = [Document(name='', text=sent.to_plain_string(), annotations=[]) for sent in sentences]
    return docs, tokens


def benchmark_tagger(tagger: TextTagger, docs: List[Document], num_tokens: int):
    durations = []

    for _ in tqdm(range(0, N_REPETITIONS), desc='Repetitions'):
        start = timer()
        tagger.annotate(docs)
        end = timer()
        durations.append(end - start)

    return {
        'mean': np.mean(durations),
        'std': np.std(durations),
        'tokens/s': num_tokens / np.mean(durations),
        'docs/s': len(docs) / np.mean(durations),
        'num_docs': len(docs),
        'num_tokens': num_tokens
    }


def main(args):
    logger.info('Load data...')
    documents, num_tokens = load_data()

    logger.info('Initialize taggers...')
    tokenizer_crf = TokenizerFactory().tokenizer(corpus='ons', disable=())
    tokenizer_bilstm = TokenizerFactory().tokenizer(corpus='ons', disable=("tagger", "ner"))

    taggers = [
        ('DEDUCE', DeduceTagger(verbose=True)),
        ('CRF', CRFTagger(
            model='model_crf_ons_tuned-v0.1.0',
            tokenizer=tokenizer_crf,
            verbose=True
        )),
        ('BiLSTM-CRF (large)', FlairTagger(
            model='model_bilstmcrf_ons_large-v0.1.0',
            tokenizer=tokenizer_bilstm,
            verbose=True
        )),
        ('BiLSTM-CRF (fast)', FlairTagger(
            model='model_bilstmcrf_ons_fast-v0.1.0',
            tokenizer=tokenizer_bilstm,
            verbose=True
        ))
    ]

    benchmark_results = []
    tagger_names = []
    for tagger_name, tagger in taggers:
        logger.info(f'Benchmark inference for tagger: {tagger_name}')
        scores = benchmark_tagger(tagger, documents, num_tokens)
        benchmark_results.append(scores)
        tagger_names.append(tagger_name)

    df = pd.DataFrame(data=benchmark_results, index=tagger_names)
    df.to_csv(f'{args.benchmark_name}.csv')
    logger.info('\n{}', df)


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("benchmark_name", type=str, help="Name of the benchmark.")
    return parser.parse_args()


if __name__ == '__main__':
    main(arg_parser())
