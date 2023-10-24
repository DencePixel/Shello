import rollbar
import sys
import os
from dotenv import load_dotenv
load_dotenv()

rollbar.init(
    access_token=os.getenv("ROLLBAR_TOKEN"),
    environment='testenv',
    code_version='1.0'
)

def payload_handler(payload, **kw):
    payload['data']['person'] = {
        'id': '1234',
        'username': 'testuser',
        'email': 'user@email',
    }

    payload['data']['custom'] = {
        'trace_id': 'aabbccddeeff',
        'feature_flags': [
            'feature_1',
            'feature_2',
        ],
    }

    return payload

rollbar.events.add_payload_handler(payload_handler)

def custom_exception_handler(type, value, traceback):
    rollbar.report_exc_info((type, value, traceback))

sys.excepthook = custom_exception_handler

a = None
a.hello()