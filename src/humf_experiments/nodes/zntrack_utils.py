# pyright: reportReturnType=false

import zntrack


def zop(path) -> str:
    return zntrack.outs_path(zntrack.nwd / path)
