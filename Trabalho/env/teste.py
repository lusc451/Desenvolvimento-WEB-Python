import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        host=os.getenv('MYSQL_HOST'),
        port=os.getenv('MYSQL_PORT'),
        database=os.getenv('MYSQL_DATABASE')
    )
    print("Conexão com o banco de dados estabelecida com sucesso.")
    conn.close()
except Exception as e:
    print("Erro ao conectar ao banco de dados:", e)
