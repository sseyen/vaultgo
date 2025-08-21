#!/usr/bin/env python3

import os
import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_db():
    db_config = {
        'host': os.environ.get('POSTGRES_HOST', 'localhost'),
        'port': os.environ.get('POSTGRES_PORT', '5432'),
        'database': os.environ.get('POSTGRES_DB', 'postgres'),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD', ''),
    }
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            conn = psycopg2.connect(**db_config)
            conn.close()
            return
        except OperationalError:
            attempt += 1
            time.sleep(1)
    
    raise Exception("Database connection failed after maximum attempts")

if __name__ == "__main__":
    wait_for_db()
