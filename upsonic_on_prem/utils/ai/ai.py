

import os

from dotenv import load_dotenv
import requests

load_dotenv(dotenv_path=".env")


this_dir = os.path.dirname(os.path.abspath(__file__))



import ollama



class AI_:
    def __init__(self):
        pass


    def gemmma(self, input_text):
        print("Gemma q:", input_text)
        response = ollama.chat(model='gemma-2b-upsonic', messages=[
        {
            'role': 'user',
            'content': input_text,
        },
        ])
        result = response['message']['content']
        print("Gemma r:", result)

        return result


    def code_to_time_complexity(self, code):
        input_text = f"Calculate the time complexity of this code: \n {code}"


        result = self.gemmma(input_text)
        return result

    def code_to_documentation(self, code):
        input_text = f"The documentation of this code: \n {code}"


        result = self.gemmma(input_text)
        return result

AI = AI_()
