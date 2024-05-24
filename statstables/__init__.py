from statstables import tables, renderers, utils

__all__ = ["params"]


class Params(dict):
    def __init__(self, *args, **kwargs) -> None:
        self.update(*args, **kwargs)

    def _set(self, key, val):
        dict.__setitem__(self, key, val)

    def _get(self, key):
        return dict.__getitem__(self, key)


params = Params()
params["ascii_padding"] = 2
