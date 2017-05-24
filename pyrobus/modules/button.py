from .module import Module, Input


class Button(Module):
    state = Input()

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Button', id, alias, robot)
