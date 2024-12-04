import pandas as pd
from transitions import Machine, State
import time
from task_manager import TaskManager


class AcademicAdvisor(Machine):
    def __init__(self):
        self.task_manager = TaskManager()
        self.user_db = pd.read_csv("Users.csv")
        self.log = []
        Machine.__init__(self, initial='INITIAL_DUMMY', send_event=True,
                         on_final='remove_from_machine')
        self.load_states()
        self.load_transitions()
        self.user_name = None
        self.plan = None


    def load_states(self):
        self.add_state(State('START'))
        self.add_state(State('IDEA_CHECK'))
        self.add_state(State('SMART_PLANNING'))
        self.add_state(State('BEHAVIOR_MEN'))
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

    def get_plan_details(self):
        self.plan = self.log_interaction("With your permission, may I ask more details? What, When, Where, How often, and Start Date?")

    def log_interaction(self, text):
        self.log.append("Advisor: " + text)
        response = input(text)
        self.log.append("Student: " + response)
        return response

    def log_output(self, text):
        self.log.append("Advisor: " + text)
        print(text)

    def get_name(self, event):
        self.user_name = self.log_interaction("Please enter your name: ")
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
        with open('log.txt', 'a') as file:
            file.write(time.ctime())
            for line in self.log:
                file.write(line)
        self.remove_model(self)
        print("Model removed")

    def get_user_idea_choice(self,event):
        self.log_output("If you're not sure, I can suggest some ideas:")
        ideas = self.task_manager.generate_ideas()
        self.log_output(ideas)
        response = self.log_interaction("Please let me know which one you would like!\n")
        idea_selection = self.task_manager.verify_ideas(ideas,response)
        print(idea_selection)

    def handle_error(self, event):
        print("an error has occurred")
        print(event.error)
        self.remove_from_machine(event)
