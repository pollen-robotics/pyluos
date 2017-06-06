from .module import Module, Input


class Button(Module):
    state = Input({
        'pressed': lambda evt: (evt.old_val != evt.new_val and
                                evt.new_val == 1),
        'released': lambda evt: (evt.old_val != evt.new_val and
                                 evt.new_val == 0),
    })

    def __init__(self, id, alias, robot):
        Module.__init__(self, 'Button', id, alias, robot)
