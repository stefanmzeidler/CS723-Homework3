import spacy_llm
from spacy_llm.util import assemble

class Confidence:
    def __init__(self):
        self.nlp = assemble("Config/confidence.cfg")

    def analyze(self,text):
        doc = self.nlp(text)
        return doc._.sentiment
