import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from peewee import PostgresqlDatabase
import os


scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]

database_name = os.getenv('DATABASE_NAME', 'default_db_name')
database_user = os.getenv('DATABASE_USER', 'default_user')
database_password = os.getenv('DATABASE_PASSWORD', 'default_password')
database_host = os.getenv('DATABASE_HOST', 'localhost')
database_port = os.getenv('DATABASE_PORT', 5432)

pg_db = PostgresqlDatabase(
    database_name,
    user=database_user,
    password=database_password,
    host=database_host,
    port=database_port
)
pg_db.connect()

query = 'SELECT * FROM googleapi'

cursor = pg_db.execute_sql(query)

json = cursor.fetchone()[0]

pg_db.close()


credentials = ServiceAccountCredentials.from_json_keyfile_dict(json, scope)
client = gspread.authorize(credentials)
