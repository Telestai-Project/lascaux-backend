.PHONY: run install 

install:
	pip install -r requirements.txt

run_app:
	python3 app/start_application.py

run_bot:
	python3 app/start_bot.py
