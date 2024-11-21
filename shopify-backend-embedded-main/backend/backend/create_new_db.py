from os import environ
from dotenv import load_dotenv

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from aws_secrets_manager import get_secret

load_dotenv()

default_db_name = 'postgres'


use_aws_secret_manager = False

if use_aws_secret_manager:
    db_name = environ.get('DB_NAME')
    aws_secret = get_secret()
    con = psycopg2.connect(
        dbname=default_db_name,
        host=environ.get('DB_HOST'),
        user=aws_secret['username'],
        password=aws_secret['password'],
        port=environ.get('DB_PORT'),
    )

else:
    db_name = environ.get('POSTGRES_DB')
    con = psycopg2.connect(
        dbname=default_db_name,
        host=environ.get('POSTGRES_HOST'),
        user=environ.get('POSTGRES_USER'),
        password=environ.get('POSTGRES_PASSWORD'),
        port=environ.get('POSTGRES_PORT'),
    )

con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cur = con.cursor()

cur.execute(sql.SQL("CREATE DATABASE {}").format(
    sql.Identifier(db_name))
)
