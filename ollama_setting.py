import os

from dotenv import load_dotenv


load_dotenv(dotenv_path=".env")

main_model_cpu = os.environ.get("main_model_cpu")

if main_model_cpu != None:
    # append num_thread to the end of the Modelfile
    with open("Modelfile", "a") as f:
        f.write(f"\nPARAMETER num_thread {main_model_cpu}")