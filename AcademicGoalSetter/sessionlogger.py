import spacy_llm
import logging
import os
import openai
from dotenv import load_dotenv


class SessionLogger:
    def __init__(self):
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        spacy_llm.logger.addHandler(logging.StreamHandler())
        spacy_llm.logger.addHandler(logging.FileHandler('log.txt'))
        spacy_llm.logger.setLevel(logging.DEBUG)

    @staticmethod
    def log_llm_interaction_start():
        spacy_llm.logger.debug("LLM Interaction Start")

    @staticmethod
    def log_llm_interaction_end():
        spacy_llm.logger.debug("LLM Interaction end")