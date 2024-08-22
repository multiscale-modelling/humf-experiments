# pyright: reportReturnType=false

from pathlib import Path

import zntrack as zn


def zop(path) -> str:
    return zn.outs_path(Path("outputs", zn.nwd, path))
