import copy


class ICloneable():
    def __init__(self):
        pass

    def clone(self):
        return copy.deepcopy(self)
