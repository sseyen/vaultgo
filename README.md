# VaultGo

VaultGo is a minimal cloud storage service built with Django and PostgreSQL. Uploaded files are encrypted on disk and served through the Django backend. The project ships with Docker so it can be started with a few commands.

## Tools
- Python / Django
- PostgreSQL
- Docker Compose

## How to run

```bash
docker compose build
docker compose up
```

You can also run the application without Docker:

```bash
pip install -r requirements.txt
cd vaultgo_project
python manage.py runserver 0.0.0.0:8000
```
