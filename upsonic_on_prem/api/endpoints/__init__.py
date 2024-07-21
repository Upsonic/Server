import importlib.util
import os

# Define the path to the pages directory
pages_dir = os.path.dirname(__file__)

# Initialize the urls and pages lists
urls_endpoints = []
user_urls_endpoints = []
scope_write_auth_endpoints = []
scope_read_auth_endpoints = []

# List all subdirectories in the pages directory
for subdir in os.listdir(pages_dir):
    subdir_path = os.path.join(pages_dir, subdir)
    if os.path.isdir(subdir_path):
        page_file = os.path.join(subdir_path, "endpoint.py")
        if os.path.isfile(page_file):
            # Import the page.py file
            module_name = f"upsonic_on_prem.api.endpoints.{subdir}.endpoint"
            spec = importlib.util.spec_from_file_location(
                module_name, page_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            urls_endpoints.append(module.url)
            if module.auth == "user":
                user_urls_endpoints.append(module.url)
                if module.scope_write_auth:
                    scope_write_auth_endpoints.append(module.url)
                if module.scope_read_auth:
                    scope_read_auth_endpoints.append(module.url)
