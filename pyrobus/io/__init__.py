import json


class IOHandler(object):
    @classmethod
    def is_host_compatible(cls, host):
        return False

    def __init__(self, host):
        raise NotImplementedError

    def read(self):
        data = self.recv()
        return self.loads(data)

    def recv(self):
        raise NotImplementedError

    def send(self, msg):
        sent_msg = self.dumps(msg)
        # print(sent_msg)
        self.write(sent_msg)

    def write(self, data):
        raise NotImplementedError

    def loads(self, data):
        try:
            if type(data) == bytes:
                data = data.decode()
            # import time
            # time.sleep(0.10)
            # # print(data)
            # import sys
            # sys.stdout.flush()
            return json.loads(data)
        except Exception as e:
            print(data)
            print(e)
            return

    def dumps(self, msg):
        return json.dumps(msg).encode()


from .ws import Ws
from .serial_io import Serial


def io_from_host(host, *args, **kwargs):
    for cls in [Ws, Serial]:
        if cls.is_host_compatible(host):
            return cls(host=host, *args, **kwargs)
    raise ValueError('No corresponding IO found.')
