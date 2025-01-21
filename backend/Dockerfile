FROM python:3.12

WORKDIR /burnote

COPY requirements/prod.txt requirements.txt

RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "manage:app", "--bind", "0.0.0.0:8000"]