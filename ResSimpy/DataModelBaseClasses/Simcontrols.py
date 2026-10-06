from typing import Any


class SimControlsBase:
    """Parent class for controlling all runcontrol related functionality."""

    def __init__(self, model: Any) -> None:
        """Initialize shared simulation-control.

        Args:
            model: Simulator model associated with these controls.
        """
        self._model = model
        self._times: list[str] | None = None
        self._number_of_processors: int | None = None
        self._drsdt_limit: float | None = None
        self._drsdt_two_phases: bool | None = None

    @property
    def model(self) -> Any:
        """Returns the simulator model associated with these controls."""
        return self._model

    @model.setter
    def model(self, value: Any) -> None:
        self._model = value

    @property
    def times(self) -> list[str]:
        """Returns the times configured for the simulation."""
        return self._times if self._times is not None else []

    @property
    def number_of_processors(self) -> int | None:
        """Returns the configured number of processors, loading them if needed."""
        if self._number_of_processors is None:
            self._load_number_of_processors()
        return self._number_of_processors

    def _load_number_of_processors(self) -> None:
        """Loads the configured number of processors for this simulator."""

    @property
    def drsdt_limit(self) -> float | None:
        """Returns the configured DRSDT limit, if available."""
        return self._drsdt_limit

    @property
    def drsdt_two_phases(self) -> bool | None:
        """Returns whether DRSDT applies only to blocks with oil and gas phases."""
        return self._drsdt_two_phases
