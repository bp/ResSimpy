ruff check ResSimpy
flake8 ResSimpy --append-config ./.config/flake8
mypy ResSimpy --config-file ./.config/mypy
pytest tests
exec $SHELL