import sys
import zmq
import json
import time
import threading

from copy import deepcopy
from datetime import datetime
from collections import defaultdict

from .io import io_from_host
from .modules import name2mod
from .metrics import Publisher


def run_from_unittest():
    return 'unittest' in sys.modules


class Robot(object):
    _heartbeat_timeout = 5  # in sec.

    def __init__(self, host,
                 verbose=True, test_mode=False,
                 *args, **kwargs):
        self._io = io_from_host(host=host,
                                *args, **kwargs)

        self._verbose = verbose

        self._log('Connected to "{}".'.format(host))

        # We force a first poll to setup our model.
        self.detect()
        self._log('Robot setup.')

        if not (test_mode or run_from_unittest()):
            self._metrics_pub = Publisher(robot=self)
            self._metrics_pub.start()

            c = zmq.Context()
            s = c.socket(zmq.PUB)
            s.connect('tcp://127.0.0.1:33000')
            self._s = s

    def detect(self):
        # TODO: why needed?
        for _ in range(2):
            self._stop_sync()

            self._log('Sending detection signal.')
            self._send({'detection': {}})

            self._log('Waiting for first state...')
            # we make it twice to prevent previous detection
            self._poll_once()
            state = self._poll_once()

            gate = next(g for g in state['modules']
                        if g['type'] == 'gate')
            self._name = gate['alias']

            modules = [mod for mod in state['modules']
                       if mod['type'] in name2mod.keys()]

            self._old_cmd = defaultdict(lambda: defaultdict(int))
            self._cmd = defaultdict(lambda: defaultdict(int))

            self.modules = [
                name2mod[mod['type']](id=mod['id'],
                                      alias=mod['alias'],
                                      robot=self)
                for mod in modules
            ]
            # We push our current state to make sure that
            # both our model and the hardware are synced.
            self._push_once()

            for mod in self.modules:
                setattr(self, mod.alias, mod)

            self._start_sync()

    def _start_sync(self):
        if not self.alive:
            # self._log('Starting synchronization.')
            # Setup both poll/push synchronization loops.
            self._last_update = time.time()
            self._running = True

            self._poll_bg = threading.Thread(target=self._poll_and_up)
            self._poll_bg.daemon = True
            self._poll_bg.start()

    def _stop_sync(self):
        if self.alive:
            # self._log('Stopping synchronization.')
            self._running = False
            self._poll_bg.join()
            self._io.flush()

    @property
    def state(self):
        return {
            'gate': self.name,
            'timestamp': datetime.now(),
            'types': ','.join([mod.type for mod in self.modules]),
            'modules': ','.join([mod.alias for mod in self.modules])
        }

    @property
    def name(self):
        return self._name

    @property
    def alive(self):
        return (hasattr(self, '_poll_bg') and
                self._running and
                (time.time() - self._last_update) < self._heartbeat_timeout)

    def close(self):
        self._stop_sync()
        self._io.close()

    # Poll state from hardware.
    def _poll_once(self):
        self._state = self._io.read()
        return self._state

    def _poll_and_up(self):
        while self._running:
            state = self._poll_once()
            self._update(state)
            self._push_once()

            self._broadcast(state)

    # Update our model with the new state.
    def _update(self, new_state):
        mod_need_update = [mod for mod in new_state['modules']
                           if hasattr(self, mod['alias']) and
                           set(mod.keys()) != {'type', 'id', 'alias'}]

        for mod in mod_need_update:
            getattr(self, mod['alias'])._update(mod)

        self._last_update = time.time()

    # Push update from our model to the hardware
    def _push_once(self):
        diff = defaultdict(dict)

        for mod, values in self._cmd.items():
            for key, val in values.items():
                if self._old_cmd[mod][key] != val:
                    diff[mod][key] = val

        if diff:
            self._send({
                'modules': diff
            })
            self._old_cmd = deepcopy(self._cmd)

    def _send(self, msg):
        self._io.send(msg)

    def _broadcast(self, state):
        if not hasattr(self, '_s'):
            return

        for mod in state['modules']:
            if ((mod['type'] in ('servo', 'dynamixel')) and
               (hasattr(self, mod['alias']))):
                servo = getattr(self, mod['alias'])
                mod['value'] = servo.position

        msg = '{} {}'.format(self.name, json.dumps(state))
        self._s.send_string(msg)

    def _log(self, msg):
        if self._verbose:
            print(msg)
