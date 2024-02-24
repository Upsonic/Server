import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

folder = os.environ.get("folder", "")
local_db_folder = os.environ.get("local_db_folder", "")
white_list_ip = os.environ.get("white_list_ip", "")
password = os.environ.get("password", "Upsonic")
threads = os.environ.get("threads", 4)
access_key = os.environ.get("access_key", "false").lower() == "true"
access_key_folder = os.environ.get("access_key_folder", "")
access_key_lists = os.environ.get("access_key_lists", "")
access_key_lists_apply = os.environ.get("access_key_apply", "false").lower() == "true"
restricted = os.environ.get("restricted", "")
restricted = restricted.split(",")


rate_limit = os.environ.get("rate_limit", "")
rate_limit = rate_limit.split(",")
key_lenght = os.environ.get("key_lenght", None)
key_lenght = int(key_lenght) if key_lenght is not None else key_lenght
value_lenght = os.environ.get("value_lenght", None)
value_lenght = int(value_lenght) if value_lenght is not None else value_lenght
database_name_lenght = os.environ.get("database_name_lenght", None)
database_name_lenght = (
    int(database_name_lenght)
    if database_name_lenght is not None
    else database_name_lenght
)
maximum_database_amount = os.environ.get("maximum_database_amount", None)
maximum_database_amount = (
    int(maximum_database_amount)
    if maximum_database_amount is not None
    else maximum_database_amount
)
maximum_key_amount = os.environ.get("maximum_key_amount", None)
maximum_key_amount = (
    int(maximum_key_amount) if maximum_key_amount is not None else maximum_key_amount
)
maximum_database_amount_user = os.environ.get("maximum_database_amount_user", None)
maximum_database_amount_user = (
    int(maximum_database_amount_user)
    if maximum_database_amount_user is not None
    else maximum_database_amount_user
)
maximum_key_amount_user = os.environ.get("maximum_key_amount_user", None)
maximum_key_amount_user = (
    int(maximum_key_amount_user)
    if maximum_key_amount_user is not None
    else maximum_key_amount_user
)











threads = os.environ.get("threads", 4)
url_scheme = os.environ.get("url_scheme", 'https')


redis_password = os.environ.get("redis_password", "Upsonic")
redis_host = os.environ.get("redis_host", "localhost")
redis_port = os.environ.get("redis_port", 6379)

admin_key = os.environ.get("admin_key")

debugging = os.environ.get("debugging", "false").lower() == "true"

sentry = os.environ.get("sentry", "false").lower() == "true"
sentry_flask_key = os.environ.get("sentry_flask_key", "https://557ac9191a887032087e4054dda517c4@o4506678585786368.ingest.sentry.io/4506678591225856")