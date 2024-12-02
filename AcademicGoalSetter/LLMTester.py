from spacy_llm.util import assemble
import os

filepath = os.path.dirname(__file__)
filepath = os.path.join(filepath, './Config/config.cfg')
print(filepath)
nlp = assemble('./Config/config.cfg')
doc = nlp("Jack and Jill rode up the hill in Les Deux Alpes")
print([(ent.text, ent.label_) for ent in doc.ents])