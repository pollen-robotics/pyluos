from collections import defaultdict


class Input(object):
    def __get__(self, instance, owner):
        return instance.__dict__.get(self.label, None)

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")


class Output(object):
    def __get__(self, instance, owner):
        return instance.__dict__.get(self.label, None)

    def __set__(self, instance, value):
        old = instance.__dict__.get(self.label, None)

        if old != value:
            instance._push_value(self.label, value)

        instance.__dict__[self.label] = value


class Plug(type):
    def __new__(cls, name, bases, attrs):
        for n, v in attrs.items():
            if isinstance(v, Input) or isinstance(v, Output):
                v.label = n

        return type.__new__(cls, name, bases, attrs)


class Module(object, metaclass=Plug):
    def __init__(self,
                 type, id, alias,
                 robot):
        self._type = type
        self.id = id
        self.alias = alias
        self._delegate = robot
        self._cb = defaultdict(list)

    def __repr__(self):
        return ('<{self._type} '
                'alias="{self.alias}" '
                'id={self.id}>'.format(self=self))

    @property
    def _state(self):
        return ('state')

    def _update(self, new_state):
        new_state.pop('id')
        new_state.pop('type')
        new_state.pop('alias')

        for key, new_val in new_state.items():
            self.__dict__[key] = new_val

    def _push_value(self, key, new_val):
        cmd = {
            self.alias: {
                key: new_val
            }
        }
        self._delegate._msg_stack.put(cmd)
