from .module import Module, Input


class Distance(Module):
    distance = Input()

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Distance', id, alias, robot)
