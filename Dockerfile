FROM python:3.9

WORKDIR /home/temperature

COPY . /home/temperature

RUN pip install poetry
RUN poetry install

CMD ["poetry", "run", "python", "/home/temperature/tasks.py"]
