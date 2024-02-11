import fire

import threading
from dotenv import load_dotenv
import traceback
from waitress import serve

if __name__ == "__main__":
    import sys
    import os

    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))



from upsonic_on_prem.api import app



from upsonic_on_prem.utils import storage


from upsonic_on_prem.utils.configs import threads, url_scheme


def api(host, port):
        global threads

        def starter():
            try:
                serve(app, host=host, port=port, threads=threads, url_scheme=url_scheme)  # pragma: no cover
            except:
                traceback.print_exc()

        threading.Thread(target=starter).start()  # pragma: no cover



if __name__ == "__main__":
    fire.Fire(api)
