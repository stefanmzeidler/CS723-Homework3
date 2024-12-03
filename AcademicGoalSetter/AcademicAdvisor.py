import enum
import pandas as pd
from transitions import Machine, State, EventData
from sessionlogger import SessionLogger
from task_manager import TaskManager


class AcademicAdvisor(Machine):
    def __init__(self):
        # self.session_logger = SessionLogger()
        # self.task_manager = TaskManager()
        self.user_db = pd.read_csv("Users.csv")
        transitions = self.load_transitions()
        Machine.__init__(self, states=self.States.values(), transitions=transitions,
                         initial=self.States.INITIAL_DUMMY.value, send_event=True, on_exception = 'to_error',on_final='remove_from_machine')
        # self.new_user = True
        self.user_name = None

    def load_transitions(self):
        transitions = [['run', self.States.INITIAL_DUMMY.value, self.States.START.value, {'after':'get_user_intention'}],
                       ['proceed_to_ideas', self.States.START.value, self.States.IDEA_CHECK.value],
                       ['help_plan',self.States.IDEA_CHECK.value,self.States.SMART_PLANNING.value],
                       ['suggest_ideas',self.States.IDEA_CHECK.value,self.States.BEHAVIOR_MENU.value],
                       ['offer_check_in',self.States.IDEA_CHECK.value,self.States.CHECK_IN_OFFER.value],
                       ['re_enter', '*', '=']]

        return transitions

    class States(enum.Enum):
        ERROR = State(name='error', on_enter = 'handle_error')
        INITIAL_DUMMY = State(name='initial_dummy', on_exit = 'get_name')
        START = State(name='start', on_enter=['get_name'])
        IDEA_CHECK = State(name='idea_check', on_enter=['print_string'])
        SMART_PLANNING = State(name='smart_planning', on_enter = 'get_goal_information')
        BEHAVIOR_MENU = State(name='behavior_menu')
        CHECK_IN_OFFER = State(name='check_in_offer')
        COMMITMENT_STATEMENT = State(name='commitment_statement')
        SUCCESS_REFLECTION = State(name='success_reflection')
        CHECK_ON_PROGRESS = State(name='check_on_progress')
        GOODBYE = State(name='goodbye')
        FINAL_DUMMY = State(name='final_dummy', final=True)

        @classmethod
        def values(cls):
            return [member.value for member in cls]

    def get_name(self, event):
        if self.States.INITIAL_DUMMY.value.name == event.transition.source:
            self.user_name = input("Please enter your name: ")
            # if self.user_name in self.user_db['names']:
            #     self.new_user = False
            # else:
        self.get_user_intention()
        # self.proceed_to_ideas()

    def print_string(self):
        print("HI")

    def get_user_intention(self, new_user = True):
        print("Are there any academic goals you would like to achieve in the next week or two?")
        response = input("Please enter yes, no, or not sure:\n")
        response = response.lower().strip()
        match response:
            case 'yes':
                self.help_plan()
            case 'no':
                self.check_in_offer()
            case 'not sure':
                self.suggest_ideas()
            case _:
                print("I'm sorry, I didn't understand that")
                self.re_enter()

    def remove_from_machine(self, event=None):
        self.remove_model(self)
        print("Model removed")

    def get_states(self):
        return self.states


def main():
    my_machine = AcademicAdvisor()


main()
