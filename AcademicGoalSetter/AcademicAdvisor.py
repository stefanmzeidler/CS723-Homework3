import enum
import pandas as pd
from transitions import Machine, State, EventData
from enum import Enum, auto
from sessionlogger import SessionLogger
from task_manager import TaskManager


class AcademicAdvisor(Machine):
    def __init__(self):
        # self.session_logger = SessionLogger()
        self.task_manager = TaskManager()
        self.user_db = pd.read_csv("Users.csv")
        self.log = []
        Machine.__init__(self, states=self.load_states(), initial='INITIAL_DUMMY', send_event=True,
                         on_final='remove_from_machine')
        self.apply_transitions()
        self.user_name = None

    def load_states(self):
        states = [
            'START',
            'IDEA_CHECK',
            'SMART_PLANNING',
            'BEHAVIOR_MENU',
            'CHECK_IN_OFFER',
            'COMMITMENT_STATEMENT',
            'SUCCESS_REFLECTION',
            'CHECK_ON_PROGRESS',
            'GOODBYE']
        return [State(state) for state in states]

    def apply_transitions(self):

        self.add_transition('run', 'INITIAL_DUMMY', 'START', after='get_name')
        self.add_transition('begin_session', 'START', 'IDEA_CHECK')
        self.on_enter_IDEA_CHECK('get_user_intention')
        self.add_transition('re_enter', '*', '=')
        self.add_transition('generate_behavior_menu','IDEA_CHECK', 'BEHAVIOR_MENU')
        # self.add_transition('get_name', self.States.IDEA_CHECK, self.get_name)
        self.on_enter_BEHAVIOR_MENU('get_user_idea_choice')
        # transitions = [['run', self.States.INITIAL_DUMMY.value, self.States.START.value, {'after':'get_name'}],
        #                ['proceed_to_ideas', self.States.START.value, self.States.IDEA_CHECK.value,],#{'after': 'get_user_intention'}
        #                ['help_plan',self.States.IDEA_CHECK.value,self.States.SMART_PLANNING.value],
        #                ['suggest_ideas',self.States.IDEA_CHECK.value,self.States.BEHAVIOR_MENU.value],
        #                ['offer_check_in',self.States.IDEA_CHECK.value,self.States.CHECK_IN_OFFER.value],
        #                ['offer_check_in',self.States.IDEA_CHECK.value,self.States.CHECK_IN_OFFER.value],
        #                ['re_enter', '*', '=']]


    class States(Enum):
        # ERROR = State(name='error', on_enter = 'handle_error')
        # INITIAL_DUMMY = State(name='initial_dummy')
        # START = State(name='start')
        # IDEA_CHECK = State(name='idea_check', on_enter=['print_string'])
        # SMART_PLANNING = State(name='smart_planning', on_enter = 'get_goal_information')
        # BEHAVIOR_MENU = State(name='behavior_menu')
        # CHECK_IN_OFFER = State(name='check_in_offer')
        # COMMITMENT_STATEMENT = State(name='commitment_statement')
        # SUCCESS_REFLECTION = State(name='success_reflection')
        # CHECK_ON_PROGRESS = State(name='check_on_progress')
        # GOODBYE = State(name='goodbye')
        # FINAL_DUMMY = State(name='final_dummy', final=True)
        INITIAL_DUMMY = auto()
        START = auto()
        IDEA_CHECK = auto()
        SMART_PLANNING = auto()
        BEHAVIOR_MENU = auto()
        CHECK_IN_OFFER = auto()
        COMMITMENT_STATEMENT = auto()
        SUCCESS_REFLECTION = auto()
        CHECK_ON_PROGRESS = auto()
        GOODBYE = auto()
        FINAL_DUMMY = auto()

        @classmethod
        def values(cls):
            return [member.value for member in cls]

    def log_interaction(self, text):
        self.log.append("Advisor: " + text)
        response = input(text)
        self.log.append("Student: " + response)
        print(self.log)
        return response

    def log_output(self, text):
        self.log.append(text)
        print(text)

    def get_name(self, event):
        self.user_name = self.log_interaction("Please enter your name: ")
        self.begin_session(first_run=True)

    def print_string(self):
        print("HI")

    def get_user_intention(self, event):
        # print("Are there any academic goals you would like to achieve in the next week or two?")
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
        print(event.error)


def main():
    my_machine = AcademicAdvisor()

# main()
