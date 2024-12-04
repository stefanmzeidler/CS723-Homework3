from stanza.server import CoreNLPClient
import stanza
import pandas as pd
text = "I want to start meeting with my advisor to help me prepare for tests."

# nlp = stanza.Pipeline('en', processors='tokenize,lemma,mwt,pos,depparse,ner')

# doc = nlp(text)
# for sentence in doc.sentences:
#     print(sentence.ents)


with CoreNLPClient(
        annotators=['tokenize', 'pos', 'lemma','ner', 'depparse','natlog', 'openie'],
        timeout=30000,
        memory='6G',
        threads = 1,
        output_format="json") as client:
        ann = client.annotate(text)
        client.stop()
for sentence in ann['sentences']:
        print(sentence['openie'])
        print(sentence['entitymentions'])

exit()