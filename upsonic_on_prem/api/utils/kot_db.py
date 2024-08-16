import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")


from kot import KOT

kot_db_ = KOT("api")


if not kot_db_.get("default_model"):
    kot_db_.set("default_model", os.environ.get("default_model", "upsonic_local_model"))


kot_db = kot_db_
