import spacy
from spacy_llm.util import assemble
from spacy.pipeline.ner import DEFAULT_NER_MODEL, EntityRecognizer
from spacy.vocab import Vocab


class TaskManager:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_md')
        self.confidence_analyzer = assemble("Config/confidence.cfg")
        self.multi_tasker = assemble("Config/multi_task.cfg")
        self.classifier = assemble("Config/check_affirmative_response.cfg")
        self.ner = EntityRecognizer(self.nlp.vocab, DEFAULT_NER_MODEL)


    def confidence_level(self,statement):
        doc = self.confidence_analyzer(statement)
        return doc._.sentiment

    def get_user_intention(self, name, first_run):

        if first_run:
            greet = "Greet them by name."
        else:
            greet = "You have already greeted them, do not greet them again."
        prompt = f"You are a warm and friendly academic advisor. You are meeting with {name}. {greet} Determine if they have any academic goals they would like to plan in the next two weeks."
        doc = self.multi_tasker(prompt)
        return doc._.llm_reply
        # return doc._.text

    def generate_ideas(self):
        prompt = "You are a warm and friendly academic advisor. Suggest three ideas for academic goals for the student for the next two weeks."
        doc = self.multi_tasker(prompt)
        return doc._.llm_reply

    def verify_ideas(self, ideas, response):
        prompt = (f" The text surrounded by ''' are three ideas for academic goals for a student for the next two weeks.\n\n '''{ideas}'''"
                  f"\n\nThe student responded with: {response}\n\nRespond with which one of the ideas the most closely matches the student's choice. Only include the idea and remove the number, nothing else.")
        doc = self.multi_tasker(prompt)
        return doc._.llm_reply

    def check_affirmative_response(self, response):
        doc = self.classifier(response)
        return next((key for key, value in (doc.cats or {}).items() if value == 1.0), None)