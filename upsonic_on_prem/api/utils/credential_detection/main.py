import os
import tempfile

from detect_secrets import SecretsCollection
from detect_secrets.core.scan import scan_file
from detect_secrets.settings import default_settings


def detect_credentials(code):
    """

    :param code:

    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmpfile:
        tmpfile.write(code.encode("utf-8"))
        tmpfile.close()

        secrets = SecretsCollection()
        with default_settings():
            secrets.scan_file(tmpfile.name)

        os.remove(tmpfile.name)
        return bool(secrets)
