import mysql.connector
import sys

def default_settings():
    conn = mysql.connector.connect(
        user='root',
        host='localhost',
        password='',
        database='las_palmas_medical_center'
    )
    return conn
