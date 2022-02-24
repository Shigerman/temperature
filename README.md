# temperature
Flask app showing statistics on air temperature in Moscow

### user can
* get current air temperature
* get comparison of current air temperature to maximum and minimum
  air temperatures for the current date in the last 80 years
* get average air temperature for a chosen date in a year
* get invaluable advice from Henky cat depending on the temperature

### instruments used
* Python and Flask for backend
* Poetry for virtual environment
* Celery for adding new temperature values daily
* Pytest for testing

### screen layout


### running the app
```
python3 -m pip install poetry
poetry install
poetry run python app.py
```

run redis-server: run "redis-server" command in the command line.
start worker: celery -A tasks worker --loglevel=INFO

### filling the database


### testing the app
