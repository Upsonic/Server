

import os

from dotenv import load_dotenv
import requests

load_dotenv(dotenv_path=".env")


this_dir = os.path.dirname(os.path.abspath(__file__))






class AI_:
    def __init__(self):
        pass


    def gemmma(self, input_text):
        print("Gemma q:", input_text)
        data = {"model":"gemma-2b-it", "prompt":input_text, "stream": False}
        result  = requests.post("http://localhost:11434/api/generate", data=data)
        print("Gemma r:", result)
        return result


    def code_to_time_complexity(self, code):
        input_text = f"Calculate the time complexity of this code: \n {code}"

        the_text = f"""
<start_of_turn>user
{input_text} <end_of_turn>
<start_of_turn>model
"""

        result = self.gemmma(the_text)
        return result

    def code_to_documentation(self, code):
        input_text = f"The documentation of this code: \n {code}"

        the_text = f"""
<start_of_turn>user
{input_text} <end_of_turn>
<start_of_turn>model
"""

        result = self.gemmma(the_text)
        return result

AI = AI_()
