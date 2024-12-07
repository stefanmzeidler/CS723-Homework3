import spacy
import re
from spacy_llm.util import assemble
from spacy_llm.pipeline import LLMWrapper
from spacy.lang.en import English
import torch
import blobfile
import transformers
import sentencepiece
import transformers.models.llama.modeling_llama as modeling_llama
import numpy as np
from nltk.chat.util import Chat, reflections


def embeddings_tester(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    no_stops = []
    for token in doc:
        if not token.is_stop:
            no_stops.append(token.text)
    new_text = " ".join(no_stops)
    doc = nlp(new_text)
    for ent in doc.ents:
        print(ent.text, ent.label_)
        # if ent.label_ == 'DATE':
        #     print("true")
        #     return
    for token in doc:
        print(token.text, token.pos_)
    # print("false")
    # for token in doc:
    #     print(token.text)
    #     print(token.pos_)

    # displacy.render(doc, style="dep", options={"distance": 100}, jupyter=True)


def main():
    # pairs = (
    #     (
    #         r"#NotTime(.*)",
    #         (
    #             "Not a Time",
    #             "Time Wrong"
    #         ),
    #     ),
    #     (
    #         r"#Time(.*)",
    #         (
    #             "A Time",
    #             "Good time"
    #         ),
    #     ),
    #     (
    #         r"#Action I(.*)",
    #         (
    #             "You %1?"
    #         ),
    #     ),
    # )

    # my_chat = Chat(pairs=pairs,reflections = reflections)
    # print(my_chat.respond("#Action I want to dance every day"))
    embeddings_tester("Before school every Tuesday")

main()
pairs = (
    (
        r"#NotTime(.*)",
        (
            "Not a Time",
            "Time Wrong"
        ),
    ),
    (
        r"#Time(.*)",
        (
            "A Time",
            "Good time"
        ),
    ),
)