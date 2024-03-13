from flask import request


def modify_token(original_token):
    # Placeholder logic for token modification
    return f"{original_token}-modified"

def edit_api_token_if_needed(req):
    api_token = req.headers.get('api_token')
    if api_token:
        modified_token = modify_token(api_token)
        # Demonstrating token modification. In a real scenario, this might involve more complex logic or direct request manipulation.
        req.headers['api_token'] = modified_token
