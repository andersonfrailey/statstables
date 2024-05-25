from statstables import tables, renderers, utils

__all__ = ["STParams"]


class Params(dict):
    def __init__(self, *args, **kwargs) -> None:
        self.update(*args, **kwargs)

    def _set(self, key, val):
        dict.__setitem__(self, key, val)

    def _get(self, key):
        return dict.__getitem__(self, key)


STParams = Params()
STParams["ascii_padding"] = 2
STParams["ascii_header_char"] = "="
STParams["ascii_footer_char"] = "-"
STParams["ascii_border_char"] = "|"
STParams["ascii_mid_rule_char"] = "-"
