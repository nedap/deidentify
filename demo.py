from deidentify.base import Document
from deidentify.taggers import FlairTagger
from deidentify.tokenizer import TokenizerFactory

# Create some text
text = (
    "Dit is stukje tekst met daarin de naam Jan Jansen. De patient J. Jansen (e: "
    "j.jnsen@email.com, t: 06-12345678) is 64 jaar oud en woonachtig in Utrecht. Hij werd op 10 "
    "oktober door arts Peter de Visser ontslagen van de kliniek van het UMCU."
)

# Wrap text in document
documents = [
    Document(name='doc_01', text=text)
]

# Select downloaded model
model = 'model_bilstmcrf_ons_fast-v0.1.0'

# Instantiate tokenizer
tokenizer = TokenizerFactory().tokenizer(corpus='ons', disable=("tagger", "ner"))

# Load tagger with a downloaded model file and tokenizer
tagger = FlairTagger(model=model, tokenizer=tokenizer, verbose=False)

# Annotate your documents
annotated_docs = tagger.annotate(documents)


from pprint import pprint

first_doc = annotated_docs[0]
pprint(first_doc.annotations)


from deidentify.util import mask_annotations

masked_doc = mask_annotations(first_doc)
print(masked_doc.text)
