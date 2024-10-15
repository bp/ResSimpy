from dataclasses import dataclass
from typing import Optional, Mapping

import pandas as pd


@dataclass(kw_only=True, repr=True)
class NexusAction:
    """A class representing a single Nexus action."""

    __action_time: str  # don't assume it is an int just yet
    __action: str
    __connection: str

    def __init__(self, action_time: str, action: str, connection: str) -> None:
        self.__action_time = action_time  # time in days the action occurred
        self.__action = action  # the specific action - can only be activate or deactivate
        self.__connection = connection  # the well/connection to perform the action on

    @property
    def action_time(self) -> str:
        return self.__action_time

    @property
    def action(self) -> str:
        return self.__action

    @property
    def connection(self) -> str:
        return self.__connection
