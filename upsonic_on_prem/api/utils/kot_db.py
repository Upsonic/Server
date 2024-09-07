import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")


from kot import KOT

kot_db_ = KOT("api", folder="/db/", enable_hashing=True)


if not kot_db_.get("default_model"):
    kot_db_.set("default_model", os.environ.get("default_model", "upsonic_local_model"))

if not kot_db_.get("default_search_model"):
    kot_db_.set("default_search_model", os.environ.get("default_search_model", "nomic-embed-text-upsonic"))


if not kot_db_.get("openai_apikey"):
    kot_db_.set("openai_apikey", os.environ.get("openai_api_key"))



if not kot_db_.get("azureopenai"):
    kot_db_.set("azureopenai", os.environ.get("azureopenai", "false").lower() == "true")



if not kot_db_.get("azureopenai_baseurl"):
    kot_db_.set("azureopenai_baseurl", os.environ.get("azureopenai_baseurl"))


if not kot_db_.get("azureopenai_key"):
    kot_db_.set("azureopenai_key", os.environ.get("azureopenai_key"))


# Ldap Settings
if not kot_db_.get("LDAP_SERVER"):
    kot_db_.set("LDAP_SERVER", os.environ.get("LDAP_SERVER"))
if not kot_db_.get("LDAP_PORT"):
    port = os.environ.get("LDAP_PORT")
    if port:
        port = int(port)
    kot_db_.set("LDAP_PORT", port)
if not kot_db_.get("LDAP_SEARCH"):
    kot_db_.set("LDAP_SEARCH", os.environ.get("LDAP_SEARCH"))
if not kot_db_.get("LDAP_BIND_USER"):
    kot_db_.set("LDAP_BIND_USER", os.environ.get("LDAP_BIND_USER"))
if not kot_db_.get("LDAP_BIND_PASSWORD"):
    kot_db_.set("LDAP_BIND_PASSWORD", os.environ.get("LDAP_BIND_PASSWORD"))

if not kot_db_.get("LDAP_USE_SSL"):
    kot_db_.set("LDAP_USE_SSL", os.environ.get("LDAP_USE_SSL", "false").lower() == "true")


if not kot_db_.get("LDAP_ACTIVE"):
    kot_db_.set("LDAP_ACTIVE", os.environ.get("LDAP_ACTIVE", "false").lower() == "true")




kot_db = kot_db_
