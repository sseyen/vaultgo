#!/bin/bash

ENV_FILE=".env"

if [ -f "$ENV_FILE" ]; then
    exit 0
fi

SECRET_KEY=$(python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(40)))")
ENCRYPTION_KEY=$(python3 -c "import base64, secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())")
DB_PASSWORD=$(python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(40)))")

cat > "$ENV_FILE" << EOF
SECRET_KEY=$SECRET_KEY
DEBUG=True
ALLOWED_HOSTS=*

POSTGRES_DB=vaultgo
POSTGRES_USER=vaultgo
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_HOST=db
POSTGRES_PORT=5432

FILE_ENCRYPTION_KEY=$ENCRYPTION_KEY
EOF
