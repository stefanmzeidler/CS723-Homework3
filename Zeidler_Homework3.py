import dataclasses
from transitions import Machine, State, EventData
from dataclasses import dataclass, astuple, asdict


class AcademicGoalSetter(Machine):
    def __init__(self):
        self.states = self.States(self)
        self.triggers = self.Triggers()
        states_list = list(self.states)
        transitions = [[self.triggers.INITIALIZE,self.states.INITIAL_DUMMY,self.states.START]]
        Machine.__init__(self, states=states_list,transitions = transitions, initial=self.states.INITIAL_DUMMY, send_event=True)
        self.initialize()

    @dataclass
    class Triggers:
        INITIALIZE: str = 'initialize'

    @dataclass
    class States:
        ERROR : State = State(name='error')
        INITIAL_DUMMY : State = State(name='initial_dummy')
        START : State= State(name='start', on_enter=['greet','get_user_action'])
        IDEA_CHECK : State= State(name='idea_check')
        SMART_PLANNING : State= State(name='smart_planning')
        BEHAVIOR_MENU : State= State(name='behavior_menu')
        CHECK_IN_OFFER : State= State(name='check_in_offer')
        COMMITMENT_STATEMENT : State= State(name='commitment_statement')
        SUCCESS_REFLECTION : State= State(name='success_reflection')
        CHECK_ON_PROGRESS : State= State(name='check_on_progress')
        GOODBYE : State= State(name='goodbye')
        FINAL_DUMMY: State = State(name='final_dummy')

        def __init__(self, outer):
            self.outer = outer

        def __iter__(self):
            return iter(list(getattr(self,  field.name) for field in dataclasses.fields(self)))

    def greet(self,event):
        print("Hello!")

    def get_user_action(self,event):
        response = input("Are there any academic goals you would like to achieve in the next week or two?\n")
        # self.route_user(event,response)

    # def route_user(self,event,response):
    #     state = event.state
    #     match state:
    #         self.states.IDEA_CHECK:
    #             print("Got it!")

def main():
    my_machine = AcademicGoalSetter()
main()
