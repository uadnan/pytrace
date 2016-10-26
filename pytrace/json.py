from __future__ import absolute_import

import json
from enum import Enum


class JsonEncoder(json.JSONEncoder):

    def default(self, o):
        if hasattr(o, 'to_json'):
            return o.to_json()

        if isinstance(o, Enum):
            return o.name

        if hasattr(o, '__dict__'):
            return o.__dict__


def dumps(o, *args, **kwargs):
    return json.dumps(o, cls=JsonEncoder, *args, **kwargs)
