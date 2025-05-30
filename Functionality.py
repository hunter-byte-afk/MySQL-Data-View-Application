
#  Functionality.py
# This file contains any functionality outside of the Graphical User Interface (GUI) that is needed for the application.

import glob
from matplotlib import table
from Database import *

# Global variables
current_database = None
current_cursor = None
current_table_widget = None

def attempt_to_connect(host, user, password, database):
    global current_database 
    current_database = Database(host, user, password, database)
    print("Created new database instance.")
    if current_database.connect():
        print("Connection successful!")
        return True
    else:
        print("Connection failed.")
        return False
    

def get_tables():
    global current_database
    global current_cursor
    print("Fetching tables from the database...")
    tables_db = []
    if current_database is None or not current_database.connection.is_connected():
        print("No active database connection.")
        return tables_db
    current_cursor = current_database.get_cursor()
    current_cursor.execute("SHOW TABLES")
    for table_name in current_cursor:
        tables_db.append(table_name[0]) 
    return tables_db
    
def view_table(table_name):
    global current_cursor
    if table_name == "procedure":
        table_name = "`procedure`"
    global current_table_widget
    if current_table_widget:
        current_table_widget.destroy()

    try:
        current_cursor = current_database.get_cursor()
        current_cursor.execute(f"SELECT * FROM {table_name}")
        rows = current_cursor.fetchall()
        columns = [desc[0] for desc in current_cursor.description]
        return rows, columns

        

    except Exception as e:
        print(f"Failed to load table '{table_name}': {e}")

def get_average_attributes(table_name):
    global current_cursor
    current_columns = []

    try:
        current_cursor = current_database.get_cursor()
        current_cursor.execute(f"Describe " + table_name)
        describe_table = current_cursor.fetchall()
        for row in describe_table:
            if "int" in row[1] or "double" in row[1] or "float" in row[1]:
                current_columns.append(row[0])
        return current_columns
    except Exception as e:
        print(f"Failed to describe table '{table_name}': {e}")
        return None

def get_average(table_name, column_name, parent_window):
    global current_cursor
    avg_answer = None
    try:
        current_cursor = current_database.get_cursor()
        current_cursor.execute(f"SELECT AVG({column_name}) FROM {table_name}")
        result = current_cursor.fetchone()
        if avg_answer:
            avg_answer.destroy()
        avg_answer = Label(parent_window, text=f"Average of {column} in {table_name}: {result[0]}", font = (default_font_family, 12))
        avg_answer.pack(pady=10)
    except Exception as e:
        print(f"Failed to calculate average for '{column_name}' in table '{table_name}': {e}")
        return None