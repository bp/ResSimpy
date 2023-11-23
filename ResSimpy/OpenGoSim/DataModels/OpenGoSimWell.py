from dataclasses import dataclass

from ResSimpy.Well import Well


@dataclass(kw_only=True)
class OpenGoSimWell(Well):
    pass
