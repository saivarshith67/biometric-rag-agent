VENV_DIR=.venv
PYTHON=$(VENV_DIR)/bin/python
UV=$(VENV_DIR)/bin/uv

# Create virtual environment
.PHONY: venv
venv:
	python3 -m venv $(VENV_DIR)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install uv


# Compile requirements.in to requirements.txt using uv
.PHONY: compile
compile:
	$(UV) pip compile --python $(PYTHON) -o requirements.txt requirements.i

# Install dependencies with uv
.PHONY: install
install:
	$(UV) pip install --python $(PYTHON) -r requirements.txt

# Lock dependencies
.PHONY: lock
lock:
	$(UV) pip compile --python $(PYTHON) -o requirements.txt pyproject.toml

.PHONY: dev-backend
dev-backend:
	PYTHONPATH=. $(VENV_DIR)/bin/uvicorn src.api.server:app --reload --host 127.0.0.1 --port 8000

# Run backend
.PHONY: run-backend
run-backend:
	$(PYTHON) -m src.main

# Run Streamlit frontend
.PHONY: frontend
frontend:
	PYTHONPATH=. streamlit run frontend/app.py


# Remove venv (for resetting)
.PHONY: clean
clean:
	rm -rf $(VENV_DIR)
