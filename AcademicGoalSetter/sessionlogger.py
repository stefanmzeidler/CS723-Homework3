import spacy_llm
import logging
import os
import openai
from dotenv import load_dotenv
import pandas as pd


class SessionLogger:
    def __init__(self):
        self.log = pd.DataFrame('')

    @staticmethod
    def log_llm_interaction_start():
        spacy_llm.logger.debug("LLM Interaction Start")

    @staticmethod
    def log_llm_interaction_end():
        spacy_llm.logger.debug("LLM Interaction end")