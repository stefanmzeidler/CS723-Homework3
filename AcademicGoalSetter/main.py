import spacy

from AcademicAdvisor import AcademicAdvisor
import os
import openai
from dotenv import load_dotenv

def main():
    load_dotenv()
    key = os.getenv("OPENAI_API_KEY")
    if key is None:
        raise RuntimeError("Please set OPENAI_API_KEY environment variable")
    openai.api_key = key
    my_advisor = AcademicAdvisor()
    my_advisor.run()
main()