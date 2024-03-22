from dataclasses import dataclass

from ResSimpy.Network import Network


@dataclass(kw_only=True, init=False)
class OpenGoSimNetwork(Network):
    # Class to be implemented later

    def __init__(self) -> None:
        """Initialises the OpenGoSimNetwork class.

        Args:
            To be implemented later.
        """
        self.nodes = None
        self.connections = None
        self.constraints = None
        self.targets = None

    def __repr__(self) -> str:
        # TODO: implement this
        return "Not implemented yet"

    def load(self) -> None:
        raise NotImplementedError("Not implemented for OGS yet")
