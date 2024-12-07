import pandas as pd
from transitions import Machine, State
import time
import os
from collections import defaultdict
import spacy
import re


class AcademicAdvisor(Machine):
    def __init__(self, debug=False):
        Machine.__init__(self, initial='INITIAL_DUMMY', send_event=True,
                         on_final='remove_from_machine')
        self.load_states()
        self.load_transitions()
        self.nlp = spacy.load("en_core_web_sm")
        self.user_name = None
        self.data_directory = "UserData"
        file_path = os.path.join(self.data_directory, 'Users.csv')
        if os.path.exists(file_path):
            self.user_db = pd.read_csv(file_path)
        else:
            self.user_db = pd.DataFrame(
                columns=["name", "idea", "what", "when", "where", "frequency", "start", "commitment"])

    def load_states(self):
        self.add_state(State('START'))
        self.add_state(State('IDEA_CHECK', on_enter='get_user_intention'))
        self.add_state(State('SMART_PLANNING'))
        self.add_state(State('BEHAVIOR_MENU', on_enter='get_user_idea_choice'))
        self.add_state(State('CHECK_IN_OFFER', on_enter='offer'))
        self.add_state(State('COMMITMENT_STATEMENT', on_enter='record_commitment'))
        self.add_state(State('CONFIDENCE_CHECK', on_enter='assess_confidence'))
        self.add_state(State('SUCCESS_REFLECTION',on_enter='reflect_on_success'))
        self.add_state(State('CHECK_ON_PROGRESS'))
        self.add_state(State('GOODBYE', on_enter ='ask_for_new_plan'))
        self.add_state(State('FINAL_DUMMY', final=True))

    def load_transitions(self):

        self.add_transition('run', 'INITIAL_DUMMY', 'START', after='get_name')
        self.add_transition('begin_session', 'START', 'IDEA_CHECK')
        self.add_transition('re_enter', '*', '=')
        self.add_transition('generate_behavior_menu', ['IDEA_CHECK', 'CONFIDENCE_CHECK','SUCCESS_REFLECTION'], 'BEHAVIOR_MENU')
        self.add_transition('help_plan', ['IDEA_CHECK', 'BEHAVIOR_MENU', 'SUCCESS_REFLECTION'], 'SMART_PLANNING',
                            after='get_plan_details')
        self.add_transition('success_reflection','CHECK_IN_OFFER','SUCCESS_REFLECTION')
        self.add_transition('get_commitment', ['SMART_PLANNING'], 'COMMITMENT_STATEMENT')
        self.add_transition("confidence", ['COMMITMENT_STATEMENT', 'SUCCESS_REFLECTION'], 'CONFIDENCE_CHECK')
        self.add_transition('restart_advisor', 'GOODBYE', 'START', after='begin_session')
        self.add_transition('offer_check_in', ['BEHAVIOR_MENU','CONFIDENCE_CHECK','IDEA_CHECK'], 'CHECK_IN_OFFER')
        self.add_transition('farewell', 'SUCCESS_REFLECTION', 'GOODBYE')
        self.add_transition('end_session', 'GOODBYE', 'FINAL_DUMMY')
        self.add_transition('force_end_session', '*', 'FINAL_DUMMY')

    def log_interaction(self, text):
        filepath = os.path.join(self.data_directory, f'{self.user_name}.txt')
        advisor_text = "Advisor: " + text + "\n"
        with open(filepath, 'a') as log:
            log.write(advisor_text)
            while (response := input(text + "\n")) == "":
                self.log_output("Sorry, input cannot be empty.")
                log.write(advisor_text)
            if response.lower().strip() == 'exit':
                self.force_end_session()
            log.write("Student: " + response + "\n")
        return response

    def log_output(self, text, advisor=True):
        filepath = os.path.join(self.data_directory, f'{self.user_name}.txt')
        with open(filepath, 'a') as log:
            if advisor:
                log.write("Advisor: " + text + "\n")
            else:
                log.write(text + "\n")
        print(text)

    def get_name(self, event):
        while (name := input("Please enter your name: ")) == "":
            print("Sorry, name cannot be empty.")
        self.user_name = name
        self.log_output("Session start: " + time.ctime() + "\nType 'exit' to end", advisor=False)
        self.log_output(f"Hi, {self.user_name}!")
        if self.user_db.query("name == @self.user_name").empty:
            self.log_output("It's nice to meet you!")
        else:
            self.log_output("Welcome back. I hope you've been well!")
        self.begin_session(first_run=True)

    def get_user_intention(self, event):
        if event.kwargs.get('first_run') or event.kwargs.get('response') == 'reprompt':
            self.log_output("Do you have anything you would like to do for your classes in the next week or two?")
            response = self.log_interaction("Please enter yes, no, or not sure:")
            response = response.lower().strip()
        else:
            response = event.kwargs.get('response')
        match response:
            case 'yes':
                response = self.log_interaction("That's great! What is your idea?")
                if self.user_db.query("name == @self.user_name & idea == @response").empty:
                    self.log_output("That sounds like a great plan!")
                    self.help_plan(idea=response)
                else:
                    self.log_output(
                        "It seems you have already planned that idea. Did you have another idea you would like to try or would you like me to suggest some ideas?")
                    while (response := self.log_interaction(
                            "Enter 'idea' to suggest another idea or 'help' if you would like suggestions").lower().strip()) != 'idea' and response != 'help':
                        self.log_output("I'm sorry, I didn't quite understand that.")
                    assert (type(response) == str)
                    if response == 'idea':
                        self.re_enter(response='yes')
                    else:
                        self.re_enter(response='not sure')
            case 'no':
                self.offer_check_in()
            case 'not sure':
                self.log_output("If you're not sure, I can suggest some ideas:")
                self.generate_behavior_menu()
            case _:
                self.log_output("I'm sorry, I didn't quite understand that.")
                self.re_enter('reprompt')

    def get_user_idea_choice(self, event):
        if ideas := self.__generate_ideas():
            for idea in ideas:
                self.log_output(idea)
            self.log_output("Please let me know which one you would like!")
            choice = self.check_if_response_is_valid_integer("Enter the integer corresponding to the idea.", range(1, len(ideas) + 1))
            idea = ideas[choice]
            results = re.search(r"[^a-zA-Z]+(.+)", idea)
            idea = results.group(1)
            self.help_plan(idea=idea)
        else:
            self.log_output("I'm sorry, it looks like you've already tried all my ideas!")
            self.offer_check_in()

    def check_if_response_is_valid_integer(self, prompt, num_range):
        valid_answer = False
        while not valid_answer:
            try:
                choice = int(self.log_interaction(prompt))
                if choice in num_range:
                    return choice
                else:
                    self.log_output("Sorry, that number isn't valid.")
            except ValueError:
                self.log_output("I'm sorry, I didn't quite understand that.")

    def __generate_ideas(self):
        ideas = ["Set aside a specific time to study and work on assignments",
                 "Go to the CEAS tutoring center in the library",
                 "Find and apply for internships",
                 "Go to office hours to get help from your professor",
                 "Don't study and hope for a miracle"]
        # df = self.user_db
        suggestions = []
        i = 0
        for idea in ideas:
            if i > 2:
                break
            if self.user_db.query("name == @self.user_name & idea == @idea").empty:
                # if df[(df["Name"] == self.user_name) & (df['idea'] == idea)].empty:
                i = i + 1
                suggestions.append(f"{i}. {idea}")
        return suggestions

    def get_plan_details(self, event):
        mydict = defaultdict(list)
        mydict['name'] = self.user_name
        mydict['idea'] = event.kwargs.get('idea')
        self.log_output(
            "Goals are a lot easier to achieve when they are clearly defined.\n"
            "A good method is to make sure that your goals are SMART.\n"
            "SMART means that goals should be Specific, Measurable, Achievable, Relevant, and Time-Bound.\n"
            "I'd like to ask you a few more questions about your idea.")
        mydict['what'].append(self.validate_response_type("Can you give a specific action you want to take?",
                                                          "I'm sorry, but that doesn't seem like an action", 'pos',
                                                          ['VERB']))
        mydict['when'].append(self.validate_response_type(
            "What time do you want to do this? E.g., on Fridays, before school every Tuesday,",
            "I'm sorry, but that doesn't seem like a time or isn't specific enough (capitalization is important).",
            'ent', ['DATE', 'TIME']))
        mydict['where'].append(self.log_interaction("Where do you want to do this?"))
        mydict['frequency'].append(self.log_interaction("How often do you want to do this?"))
        mydict['start'].append(self.validate_response_type("What date do you want to start?",
                                                           "I'm sorry, but that doesn't seem like a date.", 'ent',
                                                           ['DATE']))
        self.log_output("That sounds like a great plan!")
        self.get_commitment(dict=mydict)

    def validate_response_type(self, query, reprompt, label_type, label_names: list):
        while not self.validation_helper(self.nlp(response := self.log_interaction(query)),
                                         label_type, label_names):
            self.log_output(reprompt)
        return response

    def validation_helper(self,doc, label_type, label_names: list):
        match label_type:
            case "ent":
                doc = self.__remove_stops_helper(doc)
                for ent in doc.ents:
                    if ent.label_ in label_names:
                        return True
                return False
            case "pos":
                for token in doc:
                    if token.pos_ in label_names:
                        return True
                return False

    def __remove_stops_helper(self,doc):
        no_stops = []
        for token in doc:
            if not token.is_stop:
                no_stops.append(token.text)
        text = " ".join(no_stops)
        return self.nlp(text)

    def record_commitment(self, event):
        my_dict = event.kwargs.get('dict')
        my_dict['commitment'].append(self.log_interaction("Could you share a statement of commitment for this plan?"))
        new_entry = pd.DataFrame.from_dict(my_dict)
        if self.user_db.empty:
            self.user_db = new_entry
        else:
            self.user_db = pd.concat([self.user_db, new_entry])
        self.user_db.to_csv(os.path.join(self.data_directory, "Users.csv"), index=False)
        self.confidence()

    def assess_confidence(self, event):
        confidence = self.check_if_response_is_valid_integer("On a scale of 1 to 10, how confident are you in your plan?", range(1, 11))
        if confidence >= 7:
            self.log_output("That's great to hear!")
            self.offer_check_in()
        elif event.event.name != 're_enter':
            self.log_output("That's okay. Sometimes we are all a little anxious. Let's brainstorm a few ideas for how we can improve our confidence.")
            self.log_interaction("What are some things we can do to feel more confident?")
            self.log_output("I think those are some good ideas. Let's reassess your confidence")
            self.re_enter()
        else:
            self.log_output("Sorry to hear that you still aren't confident in your plan. Let me suggest some new ideas.")
            self.generate_behavior_menu()

    def offer(self,event):
        self.log_output("How has it been going with your plan since we last talked? Any challenges or successes you would like to share?")
        response = self.check_if_response_is_valid_string("Enter 'challenges' or 'successes'", ['challenges', 'successes'])
        match response:
            case 'challenges':
                self.log_output("I'm sorry to hear that you've been experiencing challenges. Setbacks can occur in life and I am here to help.")
                self.confidence()
            case 'match':
                self.log_output("I'm glad to hear that you've been having success with your plan!")
                self.log_interaction("What do you think contributed to this success?")
                self.success_reflection()


    def check_if_response_is_valid_string(self, prompt, options:list):
        while (response := self.log_interaction(prompt).lower().strip()) not in options:
            self.log_output("Sorry, I didn't understand that")
        return response

    def reflect_on_success(self,event):
        response = self.log_interaction("That’s fantastic to hear! What do you think helped you achieve this? Let’s build on that success!")
        self.log_output("You should keep these things in mind going forward, and I hope you experience even more success!")
        self.log_output("Do you have a new or more specific goal you'd like to so in light of your success? I can also suggest new ideas or if you are feeling good about things we can end here for today")
        response = self.check_if_response_is_valid_string("Please enter 'new goal', 'suggest ideas', or 'goodbye'",['new goal', 'suggest ideas', 'goodbye'])
        match response:
            case 'new goal':
                self.get_user_intention(response = 'yes')
            case 'suggest ideas':
                self.log_output("If you're not sure, I can suggest some ideas:")
                self.generate_behavior_menu()
            case 'goodbye':
                self.farewell()

    def ask_for_new_plan(self,event):
        self.log_output(f"It was great meeting with you today,{self.user_name}.")
        self.log_output("Please let me know if you need any additional help or if you would like to end the session for today")
        response = self.check_if_response_is_valid_string("Please enter 'help' or 'end'", options = ['help', 'end'])
        match response:
            case 'help':
                self.restart_advisor()
            case 'end':
                self.log_output("Goodbye!")
                self.log_output("Session end: " + time.ctime(), advisor=False)
                self.end_session()

    def remove_from_machine(self, event):
        self.remove_model(self)


    def handle_error(self, event):
        print("an error has occurred")
        print(event.error)
        self.remove_from_machine(event)


def main():
    my_advisor = AcademicAdvisor()
    my_advisor.run()


main()
