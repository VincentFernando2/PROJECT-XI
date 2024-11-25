import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Ganti dengan username MySQL Anda
        password="",  # Ganti dengan password MySQL Anda
        database="kfc_db"
    )
