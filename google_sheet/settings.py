import gspread
from oauth2client.service_account import ServiceAccountCredentials
from peewee import PostgresqlDatabase
from defaults.settings import settings

database_name = settings.database.name
database_user = settings.database.user
database_password = settings.database.password
database_host = settings.database.host
database_port = settings.database.port

scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]

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
