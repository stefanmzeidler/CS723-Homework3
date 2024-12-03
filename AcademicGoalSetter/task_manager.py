from spacy_llm.util import assemble


class TaskManager:
    def __init__(self):
        self.confidence_analyzer = assemble("Config/confidence.cfg")
        self.multi_tasker = assemble("Config/multi_task.cfg")
        self.classifier = assemble("Config/check_affirmative_response.cfg")

    def confidence_level(self,statement):
        doc = self.confidence_analyzer(statement)
        return doc._.sentiment

    def greet(self,name:str, met:bool):
        have_var = "have" if met else "haven't"
        prompt = f"You are a warm and welcoming academic advisor. You {have_var} met {name} before. Determine if they have any academic goals they would like to plan in the next two weeks."
        doc = self.multi_tasker(prompt)
        return doc._.text

    def check_affirmative_response(self, response):
        doc = self.classifier(response)
        return next((key for key, value in (doc.cats or {}).items() if value == 1.0), None)