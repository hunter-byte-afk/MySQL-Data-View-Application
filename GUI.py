# GUI.py
# This is the prototype that was created for C S 482: Database Management Systems's individual project phase 3.
# Author: Renae Hunt

from cProfile import label
from email.policy import default
from os import read
import select
from tkinter import *
from tkinter import ttk
from webbrowser import get
from enum import Enum
from matplotlib import style, table
from numpy import insert, pad
from scipy.__config__ import show
from settings import *
import mysql.connector
import sys
import tkinter.font as tkFont

class View_Type(Enum):
    VIEWTABLE = 1
    AVERAGE = 2
    INSERT = 3
    DELETE = 4

# Global variables
tables_db = []
root = None
db_connection = None
db_cursor = None
current_table_widget = None
selected_table = None
selected_query_type = None
selected_column = None
current_columns = []
avg_answer = None

# pretty options
default_font_family = 'Roboto'
bg_color = '#ECECEC'
accent_color = '#FEFEFE'
btn_color = '#a0c38b'
btn_hover_color = '#d0d0d0'
wh_txt_color = '#F2EFE4'
bl_txt_color = '#000000'
table_header_color = '#73a952'
font_title = (default_font_family, 20, "bold")
font_label = (default_font_family, 12)
font_button = (default_font_family, 12)
padding_x = 10
padding_y = 5



def on_quit():
    if db_connection:
        db_connection.close()
    db_cursor.close()
    db_connection.close()
    root.quit()

def submit_options(master, host, user, password, database):
    global db_connection, db_cursor, tables_db, selected_table, selected_query_type

    # Try to connect to the new database
    try:
        if db_connection:
            db_cursor.close()
            db_connection.close()

        db_connection = mysql.connector.connect(
            host=host.get(),
            user=user.get(),
            password=password.get(),
            database=database.get()
        )
        db_cursor = db_connection.cursor()
        print("Database connection updated successfully.")

        # Clear existing tables and get new ones
        tables_db.clear()
        get_tables()

        # Refresh the table selection UI
        for widget in root.winfo_children():
            if isinstance(widget, Frame):
                widget.destroy()

        # Reinitialize table buttons
        set_up_table_buttons()

    except mysql.connector.Error as err:
        print(f"Failed to connect to database: {err}")
        error_popup = Toplevel(master)
        Label(error_popup, text=f"Connection failed: {err}", fg="red", font=font_label).pack(pady=20)


def READMe_Popup():
    readme = Toplevel(root)
    readme.title("README.txt")
    readme.geometry("400x300")
    try:
        with open("README.txt", "r") as file:
            file_text = file.read()
        readme_text = Text(readme, wrap=WORD)
        readme_text.insert(1.0, file_text)
        readme_text.config(state=DISABLED)  
        readme_text.pack(expand=True, fill=BOTH)
        file.close()
    except FileNotFoundError:
        error_label = Label(readme, text="README.txt file not found.")
        error_label.pack()



def option_changes():
    options = Toplevel(root)
    options.title("Options")
    options.geometry("400x300")

    Label(options, text="Host:", font=(default_font_family, 12)).grid(row=0, column=0, sticky="e", padx=10, pady=5)
    Label(options, text="User:", font=(default_font_family, 12)).grid(row=1, column=0, sticky="e", padx=10, pady=5)
    Label(options, text="Password:", font=(default_font_family, 12)).grid(row=2, column=0, sticky="e", padx=10, pady=5)
    Label(options, text="Database:", font=(default_font_family, 12)).grid(row=3, column=0, sticky="e", padx=10, pady=5)

    _host = Entry(options)
    _user = Entry(options)
    _password = Entry(options, show="*")  
    _database = Entry(options)

    _host.grid(row=0, column=1, pady=5)
    _user.grid(row=1, column=1, pady=5)
    _password.grid(row=2, column=1, pady=5)
    _database.grid(row=3, column=1, pady=5)

    # Default values related to the original project
    _host.insert(0, "localhost")
    _user.insert(0, "root")
    _password.insert(0, "")
    _database.insert(0, "las_palmas_medical_center")

    Button(
        options, text='Submit', font=(default_font_family, 12),
        command=lambda: submit_options(options, _host, _user, _password, _database)
    ).grid(row=4, columnspan=2, pady=20)

def get_tables():
    db_cursor.execute("SHOW TABLES")
    for table_name in db_cursor:
        tables_db.append(table_name[0]) 

def set_up_table_buttons():
    selected_table = StringVar(value=tables_db[0] if tables_db else "")  

    # --- Query Type Radio Buttons ---
    query_frame = Frame(root)
    query_frame.pack(pady=10)
    query_frame.config(bg=accent_color)

    Label(query_frame, text="Select Query Type:", background = accent_color ,fg = bl_txt_color, font=(default_font_family, 24)).pack(anchor="w")

    for vt in View_Type:
        rb = Radiobutton(query_frame, text=vt.name.title(),fg = bl_txt_color, background = accent_color,font = (default_font_family, 12), variable=selected_query_type, value=vt.value)
        rb.pack(anchor="w")

    # --- Table Selection Radio Buttons ---
    radio_frame = Frame(root)
    radio_frame.config(bg=accent_color)
    radio_frame.pack(pady=10)

    max_columns = 4 
    for index, table in enumerate(tables_db):
        row = index // max_columns
        col = index % max_columns
        rb = Radiobutton(radio_frame, text=table, bg = btn_color, font = (default_font_family, 12), variable=selected_table, value=table)
        rb.grid(row=row, column=col, padx=10, pady=5, sticky="w")

    # --- Submit Button ---
    submit_btn = Button(root, text="Submit", font = (default_font_family, 12), command=lambda: run_query(selected_table.get(), selected_query_type.get()))
    submit_btn.pack(pady=10)


def view_table(table_name):
    if table_name == "procedure":
        table_name = "`procedure`"
    global current_table_widget
    if current_table_widget:
        current_table_widget.destroy()

    try:
        db_cursor.execute(f"SELECT * FROM {table_name}")
        rows = db_cursor.fetchall()
        columns = [desc[0] for desc in db_cursor.description]

        table_frame = Frame(root)
        table_frame.pack(fill=BOTH, expand=True)

        # Add vertical scrollbar
        vsb = Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=RIGHT, fill=Y)

        # Add horizontal scrollbar
        hsb = Scrollbar(table_frame, orient="horizontal")
        hsb.pack(side=BOTTOM, fill=X)

        tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                            yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.pack(fill=BOTH, expand=True)

        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        for col in columns:
            tree.heading(col,  text=col)
            tree.column(col, width=100, anchor="w")

        for row in rows:
            tree.insert('', END, values=row)

        current_table_widget = table_frame

    except Exception as e:
        print(f"Failed to load table '{table_name}': {e}")


def get_avergage_view(table_name):
    global current_columns
    global selected_column
    global avg_answer
    current_columns.clear()

    if table_name == "procedure":
        table_name = "`procedure`"
    
    try:
        db_cursor.execute("DESCRIBE " + table_name)
        describe_table = db_cursor.fetchall()
        for row in describe_table:
            if "int" in row[1] or "double" in row[1] or "float" in row[1]:
                current_columns.append(row[0])
    except Exception as e:
        print(f"Error describing table: {e}")
        return

    if not current_columns:
        warning = Toplevel(root)
        warning.title("No Numeric Columns")
        warning.geometry("300x150")
        Label(warning, text="No numeric columns to average in this table.", fg="red", font=font_label).pack(pady=20)
        Button(warning, text="OK", command=warning.destroy, font=font_button).pack(pady=10)
        return

    avg = Toplevel(root)
    avg.title("Average")
    avg.configure(bg=bg_color)
    avg_answer = None
    avg.geometry("600x400")

    Label(avg, text="Select Column for Average:", font=font_label).pack(anchor="w")
    for c in current_columns:
        rb = Radiobutton(avg, text=c, bg=btn_color, font=font_button, variable=selected_column, value=c)
        rb.pack(anchor="w")

    Button(avg, text="Submit", font=font_button, command=lambda: get_average(table_name, selected_column.get(), avg)).pack(pady=10)
    Button(avg, text="Clear", font=font_button, command=lambda: [avg_answer.destroy() if avg_answer else None]).pack(pady=10)
    Button(avg, text="Exit", font=font_button, command=avg.destroy).pack(pady=10)



def get_average(table_name, column, parent_window):
    global avg_answer  # Make sure we modify the global one
    if table_name == "procedure":
        table_name = "`procedure`"
    try:
        db_cursor.execute(f"SELECT AVG({column}) FROM {table_name}")
        result = db_cursor.fetchone()
        print(f"Average of {column} in {table_name}: {result[0]}")
        # Destroy previous answer label if it exists
        if avg_answer:
            avg_answer.destroy()
        avg_answer = Label(parent_window, text=f"Average of {column} in {table_name}: {result[0]}", font = (default_font_family, 12))
        avg_answer.pack(pady=10)
    except Exception as e:
        print(f"Failed to calculate average for '{column}' in '{table_name}': {e}")

def get_every_attribute(table_name):
    global current_columns
    if current_columns != []:
        print("Column was not empty, overwriting")
        current_columns.clear()
    if current_columns == []: 
        db_cursor.execute("Describe " + table_name)
        describe_table = db_cursor.fetchall()
        for row in describe_table:
            current_columns.append(row[0])

def insert_record(table_name, values=None):
    global current_columns

    if table_name == "procedure":
        table_name = "`procedure`"

    # Get column names
    if current_columns:
        print("Column was not empty, overwriting")
        current_columns.clear()
    get_every_attribute(table_name)

    insert_window = Toplevel(root)
    insert_window.title("Insert Record")
    insert_window.geometry("600x400")
    insert_window.configure(bg=bg_color)

    # Dictionary to hold user inputs
    entries = {}

    # Create a row for each column
    for idx, col in enumerate(current_columns):
        Label(insert_window, text=col, font = (default_font_family, 12)).grid(row=idx, column=0, padx=10, pady=5, sticky="e")
        entry = Entry(insert_window, width=30)
        entry.grid(row=idx, column=1, padx=10, pady=5)
        entries[col] = entry

    # Function to actually insert data
    def submit_insert():
        try:
            col_names = ", ".join(current_columns)
            placeholders = ", ".join(["%s"] * len(current_columns))
            values = [entries[col].get() for col in current_columns]
            query = f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders})"
            db_cursor.execute(query, values)
            db_connection.commit()
            print(f"Inserted record into {table_name}: {values}")
            Label(insert_window, text="Insert successful!", fg="green", font=font_label).grid(row=len(current_columns)+1, columnspan=2, pady=10)
        except Exception as e:
            print(f"Insert failed: {e}")
            Label(insert_window, text=f"Insert failed:\n{e}", fg="red", font=font_label, wraplength=400, justify=LEFT).grid(row=len(current_columns)+1, columnspan=2, pady=10)

        Button(insert_window, text="Submit", command=submit_insert, font = (default_font_family, 12)).grid(row=len(current_columns), columnspan=2, pady=20)


def delete_record(table_name):
    global current_columns

    if table_name == "procedure":
        table_name = "`procedure`"

    # Get current columns
    if current_columns:
        print("Column was not empty, overwriting")
        current_columns.clear()
    get_every_attribute(table_name)

    delete_window = Toplevel(root)
    delete_window.title("Delete Record")
    delete_window.geometry("600x400")
    delete_window.configure(bg=bg_color)

    primary_key_col = current_columns[0]
    Label(delete_window, text=f"Enter {primary_key_col} to delete:", font = (default_font_family, 12)).grid(row=0, column=0, padx=10, pady=20)
    id_entry = Entry(delete_window)
    id_entry.grid(row=0, column=1, padx=10, pady=20)

    def submit_delete():
        record_id = id_entry.get()
        try:
            query = f"DELETE FROM {table_name} WHERE {primary_key_col} = %s"
            db_cursor.execute(query, (record_id,))
            db_connection.commit()
            print(f"Deleted record with {primary_key_col} = {record_id}")
            Label(delete_window, text="Delete successful!", fg="green", font = (default_font_family, 12)).grid(row=2, columnspan=2, pady=10)
        except Exception as e:
            print(f"Delete failed: {e}")
            Label(delete_window, text="Delete failed.", fg="red", font = (default_font_family, 12)).grid(row=2, columnspan=2, pady=10)

    Button(delete_window, text="Delete", command=submit_delete, font = (default_font_family, 12)).grid(row=1, columnspan=2, pady=10)



def output_average_query(table_name, column):
    if table_name == "procedure":
        table_name = "`procedure`"
    try:
        db_cursor.execute(f"SELECT AVG({column}) FROM {table_name}")
        result = db_cursor.fetchone()
        print(f"Average of {column} in {table_name}: {result[0]}")
        
    except Exception as e:
        print(f"Failed to calculate average for '{column}' in '{table_name}': {e}")

def run_query(table_name, query_type_val):
    query_type = View_Type(query_type_val)
    print(f"Selected table: {table_name}, Query Type: {query_type.name}")

    if query_type == View_Type.VIEWTABLE:
        view_table(table_name)
    elif query_type == View_Type.AVERAGE:
        get_avergage_view(table_name)
    elif query_type == View_Type.INSERT:
        insert_record(table_name)
    elif query_type == View_Type.DELETE:
        delete_record(table_name)

def show_connection_prompt():
    options = Frame(root, bg=bg_color)
    options.pack(padx=padding_x, pady=padding_y)

    Label(options, text="Host:", font=font_label).grid(row=0, column=0, sticky="e", padx=10, pady=5)
    Label(options, text="User:", font=font_label).grid(row=1, column=0, sticky="e", padx=10, pady=5)
    Label(options, text="Password:", font=font_label).grid(row=2, column=0, sticky="e", padx=10, pady=5)
    Label(options, text="Database:", font=font_label).grid(row=3, column=0, sticky="e", padx=10, pady=5)

    _host = Entry(options)
    _user = Entry(options)
    _password = Entry(options, show="*")
    _database = Entry(options)

    _host.grid(row=0, column=1, pady=5)
    _user.grid(row=1, column=1, pady=5)
    _password.grid(row=2, column=1, pady=5)
    _database.grid(row=3, column=1, pady=5)

    _host.insert(0, "localhost")
    _user.insert(0, "root")
    _password.insert(0, "")
    _database.insert(0, "las_palmas_medical_center")

    Button(
        options, text='Submit', font=font_button,
        command=lambda: submit_options(root, _host, _user, _password, _database)
    ).grid(row=4, columnspan=2, pady=20)

    

def main():
    global db_connection
    global db_cursor
    global root
    global tables_db
    global selected_query_type
    global selected_column
    global avg_answer
    root = Tk()
    root.configure(bg=bg_color)
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
    style.configure("Treeview.Heading", font=font_label, background= table_header_color, foreground=bl_txt_color)
    selected_column = StringVar(value="")

    selected_query_type = IntVar(value=View_Type.VIEWTABLE.value)  


    db_connection = mysql.connector.connect(
        user='root',
        host='localhost',
        password='',
        database='las_palmas_medical_center'
    )

    db_cursor = db_connection.cursor()
    get_tables()

    try:
        db_connection = default_settings()  
        db_cursor = db_connection.cursor()
        print("Database connection established.")
    except mysql.connector.Error as err:
        print(f"Database connection failed: {err}")
        return 


    root.title("C S 482 Individual Project Phase 3") 

    # set the size of the window
    # set geometry (wxh)
    root.geometry("800x600")

    # all widgets will be here
    ## creating menu options
    menu = Menu(root)
    root.config(menu=menu)
    filemenu = Menu(menu)
    menu.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="Options", command = option_changes)
    filemenu.add_command(label="Exit", command=on_quit)

    ### this will have a pop-up that references the README file
    helpmenu = Menu(menu)
    menu.add_cascade(label='Help', menu = helpmenu)
    helpmenu.add_command(label='README', command=READMe_Popup)

    ## labels
    """ tables = Label(root, text=", ".join(tables_db))
    tables.pack() """

    ## buttons


    show_connection_prompt()

    # Execute Tkinter
    root.mainloop()

if __name__ == "__main__":
    main()