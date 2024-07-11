
import os
from dotenv import load_dotenv
import time

from upsonic_on_prem.api.utils import storage_ai_history
from upsonic_on_prem.api.utils.hashing import string_to_sha256


load_dotenv(dotenv_path=".env")


active_ai_history = os.environ.get("active_ai_history", "false").lower() == "true"





def get_all_ai_calls():
    call_dict = {}
    for each_key in storage_ai_history.keys():
        call_dict[each_key] = storage_ai_history.get(each_key)

    return call_dict

def reset_ai_calls():
    storage_ai_history.pop()


def save_ai_call(input, output, model_name):
    hash_of_call = string_to_sha256(input)
    timestampt = time.time()
    call_data = {"input": input, "output": output, "model_name": model_name}

    call_data["timestampt"] = timestampt

    storage_ai_history.set(hash_of_call, call_data)

