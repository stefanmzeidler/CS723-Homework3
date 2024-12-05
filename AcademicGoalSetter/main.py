import spacy
from spacy_llm.util import assemble
from spacy_llm.pipeline import LLMWrapper
from spacy.lang.en import English
import torch
import blobfile
import transformers
import sentencepiece
import transformers.models.llama.modeling_llama as modeling_llama
import numpy as np

def embeddings_tester(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            print("true")
            return
    print("false")
    # for token in doc:
    #     print(token.text)
    #     print(token.pos_)

    # displacy.render(doc, style="dep", options={"distance": 100}, jupyter=True)



def main():
    sentiment = assemble("Config/sentiment.cfg")
    doc = sentiment("I am very happy")
    print(doc.sentiment)

    # llm = LLMWrapper(vocab=nlp.vocab, task =task, model=["open_llama_3b", "open_llama_7b", "open_llama_7b_v2", "open_llama_13b"], cache = None, save_io = False)
main()