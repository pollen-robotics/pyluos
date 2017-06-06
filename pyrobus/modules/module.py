from collections import defaultdict, namedtuple

Event = namedtuple('Event', ('name', 'old_val', 'new_val'))


class Input(object):
    def __init__(self, events={}):
        self._evt = events

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.label, None)

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")


class Output(object):
    def __init__(self, events={}):
        self._evt = events

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.label, None)

    def __set__(self, instance, value):
        old = instance.__dict__.get(self.label, None)

        if old != value:
            instance._push_value(self.label, value)

        instance.__dict__[self.label] = value


class Plug(type):
    def __new__(cls, name, bases, attrs):
        evts = defaultdict(dict)
        for n, v in attrs.items():
            if isinstance(v, Input) or isinstance(v, Output):
                v.label = 'value'
                if v._evt:
                    evts.update({v.label: v._evt})

        plug = type.__new__(cls, name, bases, attrs)
        plug._events = dict(evts)
        return plug


class Module(object, metaclass=Plug):
    def __init__(self,
                 type, id, alias,
                 robot):
        self.id = id
        self.type = type
        self.alias = alias
        self._delegate = robot
        self._cb = defaultdict(list)

    def __repr__(self):
        return ('<{self.type} '
                'alias="{self.alias}" '
                'id={self.id}>'.format(self=self))

    def _update(self, new_state):
        new_state.pop('id')
        new_state.pop('type')
        new_state.pop('alias')

        for key, new_val in new_state.items():
            old_val = self.__dict__.get(key, None)
            self.__dict__[key] = new_val

            for name, pred in self._events[key].items():
                evt = Event(name, old_val, new_val)
                if pred(evt):
                    self._emit(evt)

    def _emit(self, evt):
        print('Emit {}'.format(evt))

    def _push_value(self, key, new_val):
        cmd = {
            self.alias: {
                key: new_val
            }
        }
        self._delegate._msg_stack.put(cmd)
