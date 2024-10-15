from dataclasses import dataclass


@dataclass(kw_only=True, repr=True)
class NexusAction:
    """A class representing a single Nexus action."""

    __action_time: str  # don't assume it is an int just yet
    __action: str
    __connection: str

    def __init__(self, action_time: str, action: str, connection: str) -> None:
        """Initializes the Nexus Action attributes."""
        self.__action_time = action_time  # time in days the action occurred
        self.__action = action  # the specific action - can only be activate or deactivate
        self.__connection = connection  # the well/connection to perform the action on

    @property
    def action_time(self) -> str:
        """Property for action time attribute."""
        return self.__action_time

    @property
    def action(self) -> str:
        """Property for action attribute."""
        return self.__action

    @property
    def connection(self) -> str:
        """Property for connection attribute."""
        return self.__connection
