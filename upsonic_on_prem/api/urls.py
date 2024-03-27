status_url = "/status"


dump_url = "/dump"
dump_code_url = "/dump_code"
dump_type_url = "/dump_type"
load_url = "/load"

get_admins_url = "/get_admins"
get_users_url = "/get_users"
get_users_keys_url = "/get_users_keys"
set_name_user_url = "/set_name"
get_name_user_url = "/get_name"
add_user_url = "/add_user"

enable_user_url = "/enable_user"

disable_user_url = "/disable_user"

is_enabled_user_url = "/is_enabled_user"

id_admin_url = "/is_admin"

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
get_requirements_of_scope_url = "/get_requirements_of_scope"
get_settings_of_scope_url = "/get_settings_of_scope"


get_time_complexity_of_scope_url = "/get_time_complexity_of_scope"

get_mistakes_of_scope_url = "/get_mistakes_of_scope"

get_required_test_types_of_scope_url = "/get_required_test_types_of_scope"
get_tags_of_scope_url = "/get_tags_of_scope"
get_security_analysis_of_scope_url = "/get_security_analysis_of_scope"


get_code_of_scope_url = "/get_code_of_scope"
get_version_code_of_scope_url = "/get_version_code_of_scope"
get_version_user_of_scope_url = "/get_version_user_of_scope"

get_dump_user_of_scope_url = "/get_dump_user_of_scope"

create_document_of_scope_url = "/create_document_of_scope"
create_time_complexity_of_scope_url = "/create_time_complexity_of_scope"

create_mistakes_of_scope_url = "/create_mistakes_of_scope"
create_required_test_types_of_scope_url = "/create_required_test_types_of_scope"
create_tags_of_scope_url = "/create_tags_of_scope"
create_security_analysis_of_scope_url = "/create_security_analysis_of_scope"


create_document_of_scope_url_old = "/create_document_of_scope_old"

get_type_of_scope_url = "/get_type_of_scope"
get_python_version_of_scope_url = "/get_python_version_of_scope"

get_all_scopes_url = "/get_all_scopes"

ai_code_to_document_url = "/ai_code_to_document"

get_all_scopes_user_url = "/get_all_scopes_user"


delete_scope_url = "/delete_scope"
delete_version_url = "/delete_version"

get_dump_history_url = "/get_dump_history"
get_version_history_url = "/get_version_history"

get_module_version_history_url = "/get_module_version_history"

load_specific_dump_url = "/load_specific_dump"
load_specific_version_url = "/load_specific_version"


get_all_scopes_name_prefix_url = "/get_all_scopes_name_prefix"

create_version_url = "/create_version"
create_version_prefix_url = "/create_version_prefix"
delete_version_prefix_url = "/delete_version_prefix"

dump_requirements_url = "/dump_requirements"
dump_settings_url = "/dump_settings"
dump_python_version_url = "/dump_python_version"


search_by_documentation_url = "/search_by_documentation"

ai_completion_url = "/ai_completion"
get_default_ai_model = "/get_default_ai_model"


create_readme_url = "/create_readme"
get_readme_url = "/get_readme"


set_openai_api_key_user = "/set_openai_api_key_user"
get_openai_api_key_user = "/get_openai_api_key_user"
delete_openai_api_key_user = "/delete_openai_api_key_user"


user_urs = [create_readme_url, get_openai_api_key_user, get_default_ai_model, get_readme_url, load_url, dump_url, get_read_scopes_of_me_url, get_write_scopes_of_me_url, get_document_of_scope_url, get_settings_of_scope_url, get_requirements_of_scope_url, get_security_analysis_of_scope_url, get_required_test_types_of_scope_url, get_tags_of_scope_url, get_mistakes_of_scope_url, get_time_complexity_of_scope_url,
            create_version_url, create_version_prefix_url, search_by_documentation_url, ai_completion_url,
            get_dump_history_url, load_specific_dump_url,load_specific_version_url, get_all_scopes_name_prefix_url,
            get_type_of_scope_url, get_python_version_of_scope_url, create_document_of_scope_url, create_security_analysis_of_scope_url, create_required_test_types_of_scope_url, create_tags_of_scope_url, create_mistakes_of_scope_url, create_time_complexity_of_scope_url, create_document_of_scope_url_old,
            get_all_scopes_user_url, delete_scope_url,delete_version_url, dump_code_url, dump_requirements_url, dump_settings_url, dump_python_version_url, dump_type_url, get_version_history_url, get_module_version_history_url, get_version_code_of_scope_url, get_code_of_scope_url]
user_write_urls = [dump_url, create_document_of_scope_url, create_security_analysis_of_scope_url, create_required_test_types_of_scope_url, create_tags_of_scope_url, create_mistakes_of_scope_url, create_time_complexity_of_scope_url, create_document_of_scope_url_old, delete_scope_url,delete_version_url,
                   create_version_url, dump_code_url, dump_requirements_url, dump_settings_url, dump_python_version_url, dump_type_url]
user_read_urls = [load_url, get_document_of_scope_url, get_requirements_of_scope_url, get_settings_of_scope_url, get_security_analysis_of_scope_url, get_required_test_types_of_scope_url, get_tags_of_scope_url, get_mistakes_of_scope_url, get_time_complexity_of_scope_url, get_dump_history_url, get_type_of_scope_url, get_python_version_of_scope_url,
                  load_specific_dump_url,load_specific_version_url, get_version_history_url, get_version_code_of_scope_url, get_code_of_scope_url]
