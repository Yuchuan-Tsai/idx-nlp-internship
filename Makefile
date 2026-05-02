.PHONY: help install test test-week1 test-week2 test-week4 test-week6 test-week7 test-week8 test-week9 extract evaluate-entities clean

help:
	@echo "Available targets:"
	@echo "  install            - Install project dependencies into ./venv"
	@echo "  test               - Run the full pytest suite"
	@echo "  test-weekN         - Run tests for a specific week (1, 2, 4, 6, 7, 8, 9)"
	@echo "  extract            - Run scripts.data_extractor.run_extractor"
	@echo "  evaluate-entities  - Run scripts.data_extractor.evaluate_entity"
	@echo "  clean              - Remove __pycache__ folders"

install:
	./venv/bin/python -m pip install -r requirements.txt

test:
	./venv/bin/python -m pytest -q

test-week1:
	./venv/bin/python -m pytest tests/test_week1.py -v

test-week2:
	./venv/bin/python -m pytest tests/test_week2.py -v

test-week4:
	./venv/bin/python -m pytest tests/test_week4.py -v

test-week6:
	./venv/bin/python -m pytest tests/test_week6.py -v

test-week7:
	./venv/bin/python -m pytest tests/test_week7.py -v

test-week8:
	./venv/bin/python -m pytest tests/test_week8.py -v

test-week9:
	./venv/bin/python -m pytest tests/test_week9.py -v

extract:
	./venv/bin/python -m scripts.data_extractor.run_extractor

evaluate-entities:
	./venv/bin/python -m scripts.data_extractor.evaluate_entity

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +

	
