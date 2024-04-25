import os
from peewee import PostgresqlDatabase, Model

database_name = os.getenv('DATABASE_NAME', 'default_db_name')
database_user = os.getenv('DATABASE_USER', 'default_user')
database_password = os.getenv('DATABASE_PASSWORD', 'default_password')
database_host = os.getenv('DATABASE_HOST', 'localhost')
database_port = os.getenv('DATABASE_PORT', 5432)

db = PostgresqlDatabase(
    database=database_name,
    user=database_user,
    password=database_password,
    host=database_host,
    port=database_port,
)
db.connect()

class BaseModel(Model):
    class Meta:
        database = db
