import os
import inspect

def get_current_directory_name():
    # Get the calling frame
    frame = inspect.stack()[1]
    # Get the file path of the calling script
    caller_file_path = frame.filename
    
    if caller_file_path:
        # Get the directory path of the calling file
        caller_dir = os.path.dirname(caller_file_path)
        # Return the base name of the directory path
        return os.path.basename(caller_dir)
    
    return None