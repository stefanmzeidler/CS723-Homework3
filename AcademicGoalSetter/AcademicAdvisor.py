from operator import truediv

import pandas as pd
from transitions import Machine, State
import time
import os
from collections import defaultdict
import spacy


class AcademicAdvisor(Machine):
    def __init__(self, debug=False):
        Machine.__init__(self, initial='INITIAL_DUMMY', send_event=True,
                         on_final='remove_from_machine')
        self.load_states()
        self.load_transitions()
        self.nlp = spacy.load("en_core_web_sm")
        self.user_name = None
        # self.log = []
        if not os.path.exists("UserData/Users.csv"):
            self.user_db = pd.read_csv("UserData/Users.csv")
        else:
            self.user_db = pd.DataFrame(
                columns=["name", "idea", "what", "when", "where", "frequency", "start", "commitment"])

    def load_states(self):
        self.add_state(State('START'))
        self.add_state(State('IDEA_CHECK'))
        self.add_state(State('SMART_PLANNING'))
        self.add_state(State('BEHAVIOR_MENU'))
        self.add_state(State('CHECK_IN_OFFER'))
        self.add_state(State('COMMITMENT_STATEMENT', on_enter='record_commitment'))
        self.add_state(State('CONFIDENCE_CHECK', on_enter='assess_commitment'))
        self.add_state(State('SUCCESS_REFLECTION'))
        self.add_state(State('CHECK_ON_PROGRESS'))
        self.add_state(State('GOODBYE'))
        self.add_state(State(name='FINAL_DUMMY', final=True))

    def load_transitions(self):

        self.add_transition('run', 'INITIAL_DUMMY', 'START', after='get_name')
        self.add_transition('begin_session', 'START', 'IDEA_CHECK')
        self.on_enter_IDEA_CHECK('get_user_intention')
        self.add_transition('re_enter', '*', '=')
        self.add_transition('generate_behavior_menu', ['IDEA_CHECK', 'SUCCESS_REFLECTION'], 'BEHAVIOR_MENU')
        self.on_enter_BEHAVIOR_MENU('get_user_idea_choice')
        self.add_transition('help_plan', ['IDEA_CHECK', 'BEHAVIOR_MENU', 'SUCCESS_REFLECTION'], 'SMART_PLANNING',
                            after='get_plan_details')
        self.add_transition('get_commitment', ['SMART_PLANNING'], 'COMMITMENT_STATEMENT')
        self.add_transition("confidence", 'COMMITMENT_STATEMENT', 'CONFIDENCE_CHECK')
        self.add_transition('restart_advisor', 'GOODBYE', 'START', after='begin_session')
        self.add_transition('offer_check_in', ['BEHAVIOR_MENU', 'IDEA_CHECK'], 'CHECK_IN_OFFER')
        self.add_transition('force_end_session', '*', 'FINAL_DUMMY')

    def log_interaction(self, text):
        with open(f"UserData/{self.user_name}.txt", 'a') as log:
            log.write("Advisor: " + text + "\n")
            response = input(text + "\n")
            if response.lower().strip() == 'exit':
                self.force_end_session()
            log.write("Student: " + response + "\n")
        return response

    def log_output(self, text, advisor=True):
        with open(f"UserData/{self.user_name}.txt", 'a') as log:
            if advisor:
                log.write("Advisor: " + text + "\n")
            else:
                log.write(text + "\n")
        print(text)

    def get_name(self, event):
        self.user_name = input("Please enter your name: ")
        self.log_output("Session start: " + time.ctime() + "\nType 'exit' to end", advisor=False)
        self.log_output(f"Hi, {self.user_name}!")
        if self.user_db.query("name == @self.user_name").empty:
            self.log_output("It's nice to meet you!")
        else:
            self.log_output("Welcome back. I hope you've been well!")
        self.begin_session(first_run=True)

    def get_user_intention(self, event):
        # if event.transition.source != self.state:
        #     self.log_output(f"Hi, {self.user_name}! It's great to see you again. Do you have anything you would like to do for your classes in the next week or two?")
        self.log_output("Do you have anything you would like to do for your classes in the next week or two?")
        response = self.log_interaction("Please enter yes, no, or not sure:")
        response = response.lower().strip()
        match response:
            case 'yes':
                response = self.log_interaction("That's great! What is your idea?")
                self.log_output("That sounds like a great plan!")
                self.help_plan(response)
            case 'no':
                self.check_in_offer()
            case 'not sure':
                self.generate_behavior_menu()
            case _:
                self.log_output("I'm sorry, I didn't quite understand that.")
                self.re_enter()

    def get_user_idea_choice(self, event):
        self.log_output("If you're not sure, I can suggest some ideas:")
        if ideas := self.__generate_ideas():
            self.log_output(ideas)
            response = self.log_interaction("Please let me know which one you would like!")
            self.log_output("Great choice!")
            self.help_plan(response)
        else:
            self.log_output("I'm sorry, it looks like you've already tried all my ideas!")
            self.check_in_offer()

    def __generate_ideas(self):
        ideas = ["Set aside a specific time to study and work on assignments.",
                 "Go to the CEAS tutoring center in the library.",
                 "Find and apply for internships",
                 "Go to office hours to get help from your professor",
                 "Don't study and hope for a miracle"]
        # df = self.user_db
        suggestions = []
        i = 0
        for idea in ideas:
            if i > 3:
                break
            if self.user_db.query("name == @self.user_name & idea == @idea").empty:
                # if df[(df["Name"] == self.user_name) & (df['idea'] == idea)].empty:
                i = i + 1
                suggestions.append(f"{i}. {idea}")
        return suggestions

    def get_plan_details(self, idea):
        mydict = defaultdict(str)
        mydict['name'] = self.user_name
        mydict['idea'] = idea
        self.log_output(
            "Goals are a lot easier to achieve when they are clearly defined.\n"
            "A good method is to make sure that your goals are SMART.\n"
            "SMART means that goals should be Specific, Measurable, Achievable, Relevant, and Time-Bound.\n"
            "I'd like to ask you a few more questions about your idea.")
        # action = self.log_interaction("Can you give a specific action you want to take?")
        while not self.validate_label(self.nlp(action := self.log_interaction(
                "Can you give a specific action you want to take?")), 'pos', 'VERB'):
            self.log_output("I'm sorry, but that doesn't seem like an action. Can you try again?")
        mydict['what'] = action
        while not self.validate_label(self.nlp(action_time := self.log_interaction(
                "When do you want to do this? E.g., on Fridays, in the afternoon.")), 'ent', 'TIME'):
            self.log_output("I'm sorry, but that doesn't seem like a time. Can you try again?")
        mydict['when'] = action_time
        mydict['where'] = self.log_interaction("Where do you want to do this?")
        self.get_commitment()

    @staticmethod
    def validate_label(doc, label_type, label_text):
        match label_type:
            case "ent":
                for ent in doc.ents:
                    if ent.label_ == label_text:
                        return True
                return False
            case "pos":
                for token in doc:
                    if token.pos_ == label_text:
                        return True
                return False

    def record_commitment(self, event):
        print("Did it!")
        self.confidence()

    def assess_commitment(self, event):
        print("confidence?")

    def remove_from_machine(self, event=None):
        self.log_output("Session end: " + time.ctime(), advisor=False)
        self.remove_model(self)
        exit(0)

    def handle_error(self, event):
        print("an error has occurred")
        print(event.error)
        self.remove_from_machine(event)


def main():
    my_advisor = AcademicAdvisor()
    my_advisor.run()


main()
