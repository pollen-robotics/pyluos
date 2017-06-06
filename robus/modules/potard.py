from .module import (Module, Input)


class Potard(Module):
    position = Input()

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Potard', id, alias, robot)
