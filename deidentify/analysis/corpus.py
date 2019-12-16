import argparse
import os
from collections import Counter
from os.path import dirname, join

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from loguru import logger
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import tqdm

from deidentify.dataset.corpus_loader import CORPUS_PATH, CorpusLoader
from deidentify.tokenizer import TokenizerFactory

CMAP = plt.get_cmap("tab10")


def annotations_to_pandas(documents):
    annotations = []

    for doc in documents:
        annotations += doc.annotations

    return pd.DataFrame(annotations, columns=['text', 'start', 'end', 'tag', 'doc_id', 'ann_id'])


def analyze_documents(documents, tokenizer):
    all_tokens = []

    doc_length_sents = []
    doc_length_tokens = []
    doc_length_punct = []
    doc_annotations = []

    term_frequency = Counter()
    document_frequency = Counter()

    for doc in tqdm(documents):
        doc_annotations.append(len(doc.annotations))
        parsed = tokenizer.parse_text(doc.text)

        num_sents = len(list(filter(lambda sent: not sent[0].text.startswith('==='), parsed.sents)))
        doc_length_sents.append(num_sents)

        tokens_filtered = [t.text for t in parsed if t.text.strip() and
                           not t.text.startswith('===')]
        tokens_normalized = [t.lower() for t in tokens_filtered]
        term_frequency.update(tokens_normalized)
        document_frequency.update(set(tokens_normalized))

        all_tokens += tokens_filtered
        doc_length_tokens.append(len(tokens_filtered))
        doc_length_punct.append(
            sum(t.is_punct for t in parsed if t.text.strip() and not t.text.startswith('===')))

    return {
        'documents': len(documents),
        'all_tokens': all_tokens,

        'sentences': sum(doc_length_sents),
        'sentences_median': np.median(doc_length_sents),
        'sentences_mean': np.mean(doc_length_sents),
        'sentences_std': np.std(doc_length_sents),

        'tokens': sum(doc_length_tokens),
        'tokens_median': np.median(doc_length_tokens),
        'tokens_mean': np.mean(doc_length_tokens),
        'tokens_std': np.std(doc_length_tokens),

        'tokens_punct': sum(doc_length_punct),
        'tokens_punct_median': np.median(doc_length_punct),
        'tokens_punct_mean': np.mean(doc_length_punct),
        'tokens_punct_std': np.std(doc_length_punct),

        'term_frequency': term_frequency,
        'document_frequency': document_frequency,

        'num_annotations': sum(doc_annotations),
        'median_annotations': np.median(doc_annotations),
        'mean_annotations': np.mean(doc_annotations),
    }


def plot_phi_distribution(df_phi_stats, num_total):
    fig = plt.figure()
    ax = df_phi_stats.all_phi.sort_values().plot.barh(figsize=(12, 9), color=CMAP(0))

    plt.suptitle('PHI Tag Distribution (n = {})'.format(num_total),
                 x=0.08, y=0.94, size=14)  # , color='dimgrey')
    plt.yticks(fontsize=12)

    # add count on top of bars
    for p in ax.patches:
        ax.annotate("{} ({:.1f}%)".format(p.get_width(), (p.get_width() / num_total) * 100),
                    (p.get_x() + p.get_width(), p.get_y()),
                    xytext=(5, 5),
                    textcoords='offset points',
                    color='dimgrey')

    ax.tick_params(axis='x', colors='dimgrey')

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.spines['bottom'].set_color('dimgrey')
    ax.spines['left'].set_color('dimgrey')
    plt.ylabel('')
    plt.xlabel('Number of occurrences', size=11)

    with PdfPages(join(OUT_DIR, 'phi-tag-distribution.pdf')) as pdf:
        pdf.savefig(fig, bbox_inches='tight')


def write_doc_stats(doc_stats, file):
    print('-' * 40, file=file)
    print('Overall', file=file)
    print('-' * 40, file=file)
    print('{:<11}: {}'.format('Documents', doc_stats['documents']), file=file)
    print('-' * 40, file=file)
    print('Sentences', file=file)
    print('-' * 40, file=file)
    print('{:<11}: {:,}'.format('Total', doc_stats['sentences']), file=file)
    print('{:<11}: {}'.format('Median', doc_stats['sentences_median']), file=file)
    print('{:<11}: {:.2f}'.format('Mean', doc_stats['sentences_mean']), file=file)
    print('{:<11}: {:.2f}'.format('Std.', doc_stats['sentences_std']), file=file)
    print('-' * 40, file=file)
    print('Tokens (excluding ws., including punct.)', file=file)
    print('-' * 40, file=file)
    print('{:<11}: {:,}'.format('Total', doc_stats['tokens']), file=file)
    print('{:<11}: {}'.format('Median', doc_stats['tokens_median']), file=file)
    print('{:<11}: {:.2f}'.format('Mean', doc_stats['tokens_mean']), file=file)
    print('{:<11}: {:.2f}'.format('Std.', doc_stats['tokens_std']), file=file)
    print('-' * 40, file=file)
    print('Vocabulary (in tokens)', file=file)
    print('-' * 40, file=file)
    print('{:<11}: {:,}'.format('All', len(set(doc_stats['all_tokens']))), file=file)
    print('{:<11}: {:,}'.format(
        'Normalized', len(set(t.lower() for t in doc_stats['all_tokens']))), file=file)
    print('-' * 40, file=file)
    print('Punctuation', file=file)
    print('-' * 40, file=file)
    print('{:<11}: {:,}'.format('Total', doc_stats['tokens_punct']), file=file)
    print('{:<11}: {}'.format('Median', doc_stats['tokens_punct_median']), file=file)
    print('{:<11}: {:.2f}'.format('Mean', doc_stats['tokens_punct_mean']), file=file)
    print('{:<11}: {:.2f}'.format('Std.', doc_stats['tokens_punct_std']), file=file)
    print('-' * 40, file=file)
    print('PHI Annotations', file=file)
    print('-' * 40, file=file)
    print('{:<11}: {:,}'.format('Total', doc_stats['num_annotations']), file=file)
    print('{:<11}: {}'.format('Median', doc_stats['median_annotations']), file=file)
    print('{:<11}: {}'.format('Mean', doc_stats['mean_annotations']), file=file)

    print('\n\n', file=file)
    print('Most Common Words:\n{}\n\n'.format(doc_stats['term_frequency'].most_common()[:20]),
          file=file)
    print('Least Common Words:\n{}\n\n'.format(doc_stats['term_frequency'].most_common()[-10:]),
          file=file)


def main(args):
    corpus_loader = CorpusLoader()
    corpus = corpus_loader.load_corpus(CORPUS_PATH[args.corpus])
    logger.info(corpus)

    df_train = annotations_to_pandas(corpus.train)
    df_train['part'] = 'train'
    df_dev = annotations_to_pandas(corpus.dev)
    df_dev['part'] = 'dev'
    df_test = annotations_to_pandas(corpus.test)
    df_test['part'] = 'test'
    df_all = pd.concat([df_train, df_dev, df_test])

    df_absolute = df_all \
        .groupby(['tag', 'part']) \
        .size() \
        .unstack() \
        .sort_values(by='train', ascending=False) \
        .fillna(0) \
        .astype(int)
    df_absolute = df_absolute.add_suffix('_phi')

    df_normalized = df_absolute / df_absolute.sum()
    df_normalized = df_normalized.add_suffix('_normalized')
    df_normalized = df_normalized.fillna(0)

    df_phi_stats = pd.concat([df_absolute, df_normalized], axis=1)
    df_phi_stats['all_phi'] = df_all.tag.value_counts()
    df_phi_stats['all_phi_normalized'] = df_all.tag.value_counts(normalize=True)

    df_phi_stats.round(3).sort_values('all_phi', ascending=False).to_csv(
        join(OUT_DIR, 'phi_distribution.csv'))

    with open(join(OUT_DIR, 'phi_summary.txt'), 'w') as f:
        print('All PHI: {}'.format(len(df_all)), file=f)
        print('PHI by data split:', file=f)
        print(df_phi_stats[['dev_phi', 'test_phi', 'train_phi']].sum(), file=f)

    plot_phi_distribution(df_phi_stats, num_total=len(df_all))

    all_documents = corpus.train + corpus.dev + corpus.test
    tokenizer = TokenizerFactory().tokenizer(args.corpus, disable=['tagger', 'ner'])
    doc_stats = analyze_documents(all_documents, tokenizer)

    with open(join(OUT_DIR, 'corpus_statistics.txt'), 'w') as f:
        write_doc_stats(doc_stats, file=f)


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", help="Name of corpus (e.g., 'dummy', 'ons')", type=str)
    return parser.parse_args()


if __name__ == '__main__':
    ARGS = arg_parser()

    OUT_DIR = join(dirname(__file__), '../../output/corpus-analysis/{}'.format(ARGS.corpus))
    os.makedirs(OUT_DIR, exist_ok=True)
    main(ARGS)
