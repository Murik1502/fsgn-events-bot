import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from peewee import PostgresqlDatabase


scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]

pg_db = PostgresqlDatabase('fsgnevents', user='postgres', password='12345', host='45.12.75.8', port=5438)

pg_db.connect()

query = 'SELECT * FROM googleapi'

cursor = pg_db.execute_sql(query)

json = cursor.fetchone()[0]

pg_db.close()


credentials = ServiceAccountCredentials.from_json_keyfile_dict(json, scope)
client = gspread.authorize(credentials)
