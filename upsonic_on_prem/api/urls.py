status_url = "/status"


dump_url = "/dump"
dump_code_url = "/dump_code"
dump_type_url = "/dump_type"
load_url = "/load"

get_admins_url = "/get_admins"
get_users_url = "/get_users"

add_user_url = "/add_user"

enable_user_url = "/enable_user"

disable_user_url = "/disable_user"


enable_admin_url = "/enable_admin"

disable_admin_url = "/disable_admin"

delete_user_url = "/delete_user"

total_size_url = "/total_size"

scope_write_add_url = "/scope_write_add"
scope_write_delete_url = "/scope_write_delete"
scope_read_add_url = "/scope_read_add"
scope_read_delete_url = "/scope_read_delete"

get_read_scopes_of_user_url = "/get_read_scopes_of_user"
get_write_scopes_of_user_url = "/get_write_scopes_of_user"

can_access_read_user_url = "/can_access_read_user"
can_access_write_user_url = "/can_access_write_user"

get_read_scopes_of_me_url = "/get_read_scopes_of_me"
get_write_scopes_of_me_url = "/get_write_scopes_of_me"

get_len_of_users_url = "/get_len_of_users"

get_len_of_admins_url = "/get_len_of_admins"

scopes_write_clear_url = "/scopes_write_clear"

scopes_read_clear_url = "/scopes_read_clear"

event_url = "/event"

get_last_x_event_url = "/get_last_x_event"

get_document_of_scope_url = "/get_document_of_scope"
create_document_of_scope_url = "/create_document_of_scope"
create_document_of_scope_url_old = "/create_document_of_scope_old"

get_type_of_scope_url = "/get_type_of_scope"

get_all_scopes_url = "/get_all_scopes"

ai_code_to_document_url = "/ai_code_to_document"

get_all_scopes_user_url = "/get_all_scopes_user"


delete_scope_url = "/delete_scope"

get_dump_history_url = "/get_dump_history"
get_version_history_url = "/get_version_history"



load_specific_dump_url = "/load_specific_dump"

get_all_scopes_name_prefix_url = "/get_all_scopes_name_prefix"

create_version_url = "/create_version"

user_urs = [load_url, dump_url, get_read_scopes_of_me_url, get_write_scopes_of_me_url, get_document_of_scope_url,
            create_version_url,
            get_dump_history_url, load_specific_dump_url, get_all_scopes_name_prefix_url,
            get_type_of_scope_url, create_document_of_scope_url, create_document_of_scope_url_old,
            get_all_scopes_user_url, delete_scope_url, dump_code_url, dump_type_url, get_version_history_url]
user_write_urls = [dump_url, create_document_of_scope_url, create_document_of_scope_url_old, delete_scope_url,
                   create_version_url, dump_code_url, dump_type_url]
user_read_urls = [load_url, get_document_of_scope_url, get_dump_history_url, get_type_of_scope_url,
                  load_specific_dump_url, get_version_history_url]
