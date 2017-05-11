from .module import Module


class Potard(Module):
    possible_events = {'moved'}

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Potard', id, alias, robot)
        self._value = 0

    @property
    def position(self):
        return self._value

    def _update(self, new_state):
        new_pos = new_state['value']

        if new_pos != self._value:
            self._pub_event('moved', self._value, new_pos)
            self._value = new_pos
