import pandas as pd
from transitions import Machine, State
import time
from task_manager import TaskManager
import os
import logging



class AcademicAdvisor(Machine):
    def __init__(self, debug=False):
        self.task_manager = TaskManager()
        Machine.__init__(self, initial='INITIAL_DUMMY', send_event=True,
                         on_final='remove_from_machine')
        self.load_states()
        self.load_transitions()
        self.user_name = None
        self.plan = None
        self.log = []
        if not os.path.exists("UserData/Users.csv"):
            self.user_db = pd.read_csv("UserData/Users.csv")
        else:
            self.user_db = pd.DataFrame(columns=["User", "Goal", "Commitment"])

    def load_states(self):
        self.add_state(State('START'))
        self.add_state(State('IDEA_CHECK'))
        self.add_state(State('SMART_PLANNING'))
        self.add_state(State('BEHAVIOR_MENU'))
        self.add_state(State('CHECK_IN_OFFER'))
        self.add_state(State('COMMITMENT_STATEMENT'))
        self.add_state(State('SUCCESS_REFLECTION'))
        self.add_state(State('CHECK_ON_PROGRESS'))
        self.add_state(State('GOODBYE'))
        self.add_state(State(name = 'FINAL_DUMMY', final = True))


    def load_transitions(self):

        self.add_transition('run', 'INITIAL_DUMMY', 'START', after='get_name')
        self.add_transition('begin_session', 'START', 'IDEA_CHECK')
        self.on_enter_IDEA_CHECK('get_user_intention')
        self.add_transition('re_enter', '*', '=')
        self.add_transition('generate_behavior_menu',['IDEA_CHECK','SUCCESS_REFLECTION'], 'BEHAVIOR_MENU')
        self.on_enter_BEHAVIOR_MENU('get_user_idea_choice')
        self.add_transition('help_plan', ['IDEA_CHECK','BEHAVIOR_MENU','SUCCESS_REFLECTION'], 'SMART_PLANNING', after = 'get_plan_details')
        self.add_transition('get_commitment', ['CONFIDENCE_CHECK', 'SUCCESS_REFLECTION'], 'BEHAVIOR_MENU')
        self.add_transition('restart_advisor', 'GOODBYE', 'START', after = 'begin_session')
        self.add_transition('offer_check_in', ['BEHAVIOR_MENU', 'IDEA_CHECK'], 'CHECK_IN_OFFER')
        self.add_transition('force_end_session', '*', 'FINAL_DUMMY')

    def log_interaction(self, text):
        with open(f"UserData/{self.user_name}.txt", 'a') as log:
            log.write("Advisor: " + text+"\n")
            response = input(text)
            if response.lower().strip() == 'exit':
                self.force_end_session()
            log.write("Student: " + response+"\n")
        return response

    def log_output(self, text, advisor = True):
        with open(f"UserData/{self.user_name}.txt", 'a') as log:
            if advisor:
                log.write("Advisor: " + text + "\n")
            else:
                log.write(text+"\n")
        print(text)

    def get_name(self, event):
        self.user_name = input("Please enter your name: ")
        self.log_output("Session start: " + time.ctime() + "\nType 'exit' to end",advisor=False)
        self.begin_session(first_run=True)

    def get_user_intention(self, event):
        if event.transition.source != self.state:
            self.log_output(self.task_manager.get_user_intention(self.user_name, event.kwargs.get('first_run')))
        response = self.log_interaction("Please enter yes, no, or not sure:\n")
        response = response.lower().strip()
        match response:
            case 'yes':
                self.help_plan()
            case 'no':
                self.check_in_offer()
            case 'not sure':
                self.generate_behavior_menu()
            case _:
                self.log_output("I'm sorry, I didn't quite understand that.")
                self.re_enter()

    def remove_from_machine(self, event=None):
        self.log_output("Session end: " + time.ctime(),advisor=False)
        self.remove_model(self)
        exit(0)

    def get_user_idea_choice(self,event):
        self.log_output("If you're not sure, I can suggest some ideas:")
        ideas = self.task_manager.generate_ideas()
        self.log_output(ideas)
        response = self.log_interaction("Please let me know which one you would like!\n")
        idea_selection = self.task_manager.verify_ideas(ideas,response)


    def handle_error(self, event):
        print("an error has occurred")
        print(event.error)
        self.remove_from_machine(event)

    def get_plan_details(self):
        self.plan = self.log_interaction(
            "With your permission, may I ask more details? What, When, Where, How often, and Start Date?")