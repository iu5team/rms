import copy


class Model:
    def __init__(self, **kwargs):
        for field in kwargs:
            setattr(self, field, kwargs[field])

    def update(self):
        pass

    @staticmethod
    def get(pk):
        # type: (object) -> object
        pass

    def delete(self):
        pass

