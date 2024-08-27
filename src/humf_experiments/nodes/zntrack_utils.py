# pyright: reportReturnType=false

import zntrack as zn


def zop(path) -> str:
    return zn.outs_path(zn.nwd / path)
