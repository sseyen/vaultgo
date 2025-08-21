FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-db.py ./
COPY vaultgo_project ./vaultgo_project

WORKDIR /app/vaultgo_project

CMD ["sh", "-c", "python /app/wait-for-db.py \
    && python manage.py migrate \
    && python manage.py collectstatic --noinput \
    && python manage.py runserver 0.0.0.0:8000"]
    # && gunicorn vaultgo_project.wsgi:application --bind 0.0.0.0:8000"]
