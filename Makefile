.ONESHELL:

.PHONY: venv activate clean

all: venv activate install

VENV_NAME = .venv

venv:
	@if not exist $(VENV_NAME) ( \
		echo Creating virtual environment && \
		python -m venv $(VENV_NAME) \
	) else ( \
		echo Virtual environment already exists \
	)

activate:
	@echo "Activating virtual environment"
	.\.venv\Scripts\activate

install:
	@echo "Installing requirements"
	pip install -r requirements.txt

clean:
	@echo "Removing virtual environment"
	rd /s /q $(VENV_NAME)
