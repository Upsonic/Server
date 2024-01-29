import fire

import threading
from dotenv import load_dotenv
import traceback
from waitress import serve


from upsonic_on_prem.api import app



from upsonic_on_prem.utils import storage


from upsonic_on_prem.utils.configs import threads, url_scheme

class _cli:

    def api(sef, host, port):
        global threads

        def starter():
            try:
                serve(app, host=host, port=port, threads=threads, url_scheme=url_scheme)  # pragma: no cover
            except:
                traceback.print_exc()

        print(storage.get("test"))

        threading.Thread(target=starter).start()  # pragma: no cover





def cli():
    fire.Fire(_cli)