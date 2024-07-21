import inspect
import os

from flask import request

from upsonic_on_prem.api.app import app, jsonify


def get_current_directory_name():
    """ """
    # Get the calling frame
    frame = inspect.stack()[1]
    # Get the file path of the calling script
    caller_file_path = frame.filename

    the_return = None

    if caller_file_path:
        # Get the directory path of the calling file
        caller_dir = os.path.dirname(caller_file_path)
        # Return the base name of the directory path
        the_return = os.path.basename(caller_dir)

    if the_return is not None:
        the_return = "/" + the_return.replace("_", "/")

    return the_return


def get_scope_name(request_):
    """

    :param request_: 

    """
    scope = request_.form.get("scope")
    return scope
