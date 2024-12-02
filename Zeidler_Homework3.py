import enum

from transitions import Machine, State


class AcademicGoalSetter(Machine):
    def __init__(self):
        transitions = [[self.Triggers.INITIALIZE.value, self.States.INITIAL_DUMMY.value, self.States.START.value]]
        Machine.__init__(self, states=self.States.values(), transitions=transitions,
                         initial=self.States.INITIAL_DUMMY.value, send_event=True, on_exception = 'to_error',on_final='remove_from_machine')
        self.initialize()

    class Triggers(enum.Enum):
        INITIALIZE = 'initialize'

    class States(enum.Enum):
        ERROR = State(name='error', on_enter = 'handle_error')
        INITIAL_DUMMY = State(name='initial_dummy')
        START = State(name='start', on_enter=['greet', 'to_idea_check'])
        IDEA_CHECK = State(name='idea_check', on_enter='get_user_action')
        SMART_PLANNING = State(name='smart_planning')
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

    # @dataclass
    # class States:
    #     ERROR : State = State(name='error')
    #     INITIAL_DUMMY : State = State(name='initial_dummy')
    #     START : State= State(name='start', on_enter= ['greet', 'to_idea_check'])
    #     IDEA_CHECK : State= State(name='idea_check',on_enter='get_user_action')
    #     SMART_PLANNING : State= State(name='smart_planning')
    #     BEHAVIOR_MENU : State= State(name='behavior_menu')
    #     CHECK_IN_OFFER : State= State(name='check_in_offer')
    #     COMMITMENT_STATEMENT : State= State(name='commitment_statement')
    #     SUCCESS_REFLECTION : State= State(name='success_reflection')
    #     CHECK_ON_PROGRESS : State= State(name='check_on_progress')
    #     GOODBYE : State= State(name='goodbye')
    #     FINAL_DUMMY: State = State(name='final_dummy', final = True)
    #
    #     def __init__(self, outer):
    #         self.outer = outer
    #
    #     def __iter__(self):
    #         return iter(list(getattr(self,  field.name) for field in dataclasses.fields(self)))

    def greet(self, event):
        print("Hello!")

    def get_user_action(self, event):
        response = input("Are there any academic goals you would like to achieve in the next week or two?\n")
        self.route_user(event, response)

    def route_user(self, event, response):
        state = event.state
        print(state)
        match state:
            case self.States.IDEA_CHECK.value:
                print("Got it!")
                self.to_final_dummy()

    def remove_from_machine(self, event):
        self.remove_model(self)
        print("Model removed")

    def get_states(self):
        return self.states


def main():
    my_machine = AcademicGoalSetter()


main()
