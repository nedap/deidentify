"""Conversion script for the i2b2/UTHealth corpus."""

import glob
import os
import xml.etree.ElementTree as ET
from os.path import basename, dirname, join, splitext

from loguru import logger
from sklearn.model_selection import train_test_split

from deidentify.base import Annotation, Document
from deidentify.dataset import brat

BASE_PATH = join(dirname(__file__), '../../data/raw/i2b2/')
TRAIN_SET_A = join(BASE_PATH, 'training-PHI-Gold-Set1')
TRAIN_SET_B = join(BASE_PATH, 'training-PHI-Gold-Set2')
TEST_SET = join(BASE_PATH, 'testing-PHI-Gold-fixed')

OUTPUT_PATH = join(dirname(__file__), '../../data/corpus/i2b2/')

TAG_MAPPING = {
    # not sure why the PHI:* classes exist alongside with the other classes. This only affect 16
    # instances of PHI. The following remaps those tags.
    'PHI:PATIENT': 'NAME:PATIENT',
    'PHI:DOCTOR': 'NAME:DOCTOR',
    'PHI:DATE': 'DATE:DATE'
}

def xml_to_document(xml_file):
    """Converts an i2b2/UTHealth XML document to a `deidentify.base.Document`.

    XML Structure:
    ```
    <?xml version="1.0" encoding="UTF-8" ?>
    <deIdi2b2>
    <TEXT><![CDATA[
        this is the record content
    ]]></TEXT>
    <TAGS>
    <DATE id="P0" start="16" end="26" text="2067-05-03" TYPE="DATE" comment="" />
    <AGE id="P1" start="50" end="52" text="55" TYPE="AGE" comment="" />
    </TAGS>
    </deIdi2b2>
    ```
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    text = root.find('TEXT').text
    doc_name = 'doc-' + splitext(basename(xml_file))[0]

    annotations = []
    for tag_element in root.find('TAGS'):
        tag_name = tag_element.tag + ':' + tag_element.attrib['TYPE']
        annotations.append(Annotation(
            text=tag_element.attrib['text'],
            start=tag_element.attrib['start'],
            end=tag_element.attrib['end'],
            # Example: NAME:DOCTOR
            tag=TAG_MAPPING.get(tag_name, tag_name),
            # i2b2 annotations have id prefixed with P. Example: P12
            doc_id=doc_name,
            ann_id='T{}'.format(tag_element.attrib['id'][1:])
        ))

    return Document(name=doc_name, text=text, annotations=annotations)


def _write_documents(path, documents):
    os.makedirs(path, exist_ok=True)
    for doc in documents:
        brat.write_brat_document(path, doc.name, doc.text, doc.annotations)


def main():
    train_a = glob.glob(join(TRAIN_SET_A, '*.xml'))
    train_b = glob.glob(join(TRAIN_SET_B, '*.xml'))
    test = glob.glob(join(TEST_SET, '*.xml'))

    train_docs = [xml_to_document(xml_doc) for xml_doc in train_a + train_b]
    test_docs = [xml_to_document(xml_doc) for xml_doc in test]

    logger.info('train/test docs: {}/{}'.format(len(train_docs), len(test_docs)))

    logger.info('Take 20% of training instances as dev set...')
    train_docs, dev_docs = train_test_split(train_docs, test_size=0.2, random_state=42)
    logger.info('train/dev/test docs: {}/{}/{}'.format(
        len(train_docs), len(dev_docs), len(test_docs)))

    _write_documents(join(OUTPUT_PATH, 'train'), train_docs)
    _write_documents(join(OUTPUT_PATH, 'dev'), dev_docs)
    _write_documents(join(OUTPUT_PATH, 'test'), test_docs)

    logger.info('Done.')


if __name__ == '__main__':
    main()
