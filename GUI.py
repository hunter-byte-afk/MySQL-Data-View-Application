from tkinter import *  # noqa: F403
from tkinter import ttk
import tkinter.font as tkFont
from enum import Enum

from matplotlib.artist import get
from pyparsing import col
from Functionality import *
from Database import *


# GUI Theme
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

# Global Variables
db_tables = []
root = None
db_connection = None
db_cursor = None
current_table_widget = None
selected_table = None
selected_query_type = None
selected_column = None
current_columns = []
avg_answer = None

class View_Type(Enum):
    VIEWTABLE = 1
    AVERAGE = 2
    INSERT = 3
    DELETE = 4


# Function to run the selected query

def run_query(table_name, query_type):
    query_type = View_Type(int(query_type))
    print(f"Selected table: {table_name}, Query type: {query_type.name}")

    if query_type == View_Type.VIEWTABLE:
        populate_table_overview(table_name)
    elif query_type == View_Type.AVERAGE:
        get_average_view(table_name)
    elif query_type == View_Type.INSERT:
        pass
    elif query_type == View_Type.DELETE:
        pass

def populate_table_overview(table_name):
    if table_name == "procedure":
        table_name = "`procedure`"
    global current_table_widget
    rows, columns = view_table(table_name)  # noqa: F405

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

def get_average_view(table_name):
    global current_columns, selected_column, avg_answer, root
    current_columns.clear()
    selected_column = StringVar(value="")  # default selection


    if table_name == "procedure":
        table_name = "`procedure`"
    current_columns = get_average_attributes(table_name)  

    if not current_columns:
        warning = Toplevel(root)
        warning.title("No Numeric Columns")
        warning.geometry("300x150")
        Label(warning, text="No numeric columns found in the table.", fg = "red", font = font_label).pack(pady=20)
        Button(warning, text="OK", command=warning.destroy, font = font_button).pack(pady=10)
        return
    avg = Toplevel(root)
    avg.title("Average Calculation")
    avg.configure(bg=bg_color)
    avg.geometry("600x400")
    avg_answer = None


    Label(avg, text="Select Column for Average:", font=font_label).pack(anchor="w")
    for c in current_columns:
        rb = Radiobutton(avg, text=c, bg=btn_color, font=font_button, variable=selected_column, value=c)
        rb.pack(anchor="w")

    Button(avg, text="Submit", font=font_button, command=lambda: get_average(table_name, selected_column.get(), avg)).pack(pady=10)
    Button(avg, text="Clear", font=font_button, command=lambda: [avg_answer.destroy() if avg_answer else None]).pack(pady=10)
    Button(avg, text="Exit", font=font_button, command=avg.destroy).pack(pady=10)



def get_insert_view(table_name):
    pass
def get_delete_view(table_name):
    pass


# Pop-ups!
def READMe_Popup():
    readme = Toplevel(root)
    readme.title("README.txt")
    readme.geometry("400x300")
    try:
        with open("README.txt", "r") as file:
            file_text = file.read()
        readme_text = Text(readme, wrap=WORD)
        readme_text.insert(1.0, file_text)
        readme_text.config(state=DISABLED)  # Make the text read-only
        readme_text.pack(expand=True, fill=BOTH)
        file.close()
    except FileNotFoundError:
        error_label = Label(readme, text="README.txt file not found.")
        error_label.pack()

def change_average(table_name, column_name):
    global avg_answer, root
    average = get_average(table_name, column_name, root)
    if average:
        average.destroy()
    avg_answer = Label(parent_window, text=f"Average of {column} in {table_name}: {result[0]}", font = (default_font_family, 12))
    avg_answer.pack(pady=10)
# Functions for Connecting to the Database #

# this will activate when the user clicks the submit button
def connecting(_host, _user, _password, _database):
    print("Attempting to connect!")
    if attempt_to_connect(_host.get(), _user.get(), _password.get(), _database.get()) is True:
        print("Connection successful!")
        populate_view()

def populate_view():
    global selected_table, selected_query_type, db_tables
    for widget in root.winfo_children():
        widget.destroy()
    db_tables = get_tables()

    selected_table = StringVar(value=db_tables[0] if db_tables else "")  # default selection
    selected_query_type = StringVar(value=View_Type.VIEWTABLE.value)  
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

    max_columns = 4  # number of buttons per row before wrapping
    for index, table in enumerate(db_tables):
        row = index // max_columns
        col = index % max_columns
        rb = Radiobutton(radio_frame, text=table, bg = btn_color, font = (default_font_family, 12), variable=selected_table, value=table)
        rb.grid(row=row, column=col, padx=10, pady=5, sticky="w")

    # --- Submit Button ---
    submit_btn = Button(root, text="Submit", font = (default_font_family, 12), command=lambda: run_query(selected_table.get(), selected_query_type.get()))
    submit_btn.pack(pady=10)


def main():
    global db_connection
    global db_cursor
    global root

    root = Tk()
    root.configure(bg=bg_color)
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Treeview", background="white", foreground="black", rowheight=25, fieldbackground="white")
    style.configure("Treeview.Heading", font=font_label, background=table_header_color, foreground=bl_txt_color)

    root.title("Database Viewer")
    root.geometry("800x600")
    configMenu = Menu(root)
    configMenu.add_cascade(label = "Readme", command=READMe_Popup)
    configMenu.add_separator()
    root.config(menu=configMenu)
    configMenu = Menu(configMenu, tearoff=0)

    options = Frame(root, bg=bg_color)
    options.pack(padx=padding_x, pady=padding_y)

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

    # Optional: Pre-fill with default values
    _host.insert(0, "localhost")
    _user.insert(0, "root")
    _password.insert(0, "")
    _database.insert(0, "las_palmas_medical_center")

    Button(
        options, text='Submit', font=(default_font_family, 12),
        command=lambda: connecting(_host, _user, _password, _database)
    ).grid(row=4, columnspan=2, pady=20)    

    
    root.mainloop()



if __name__ == "__main__":
    main()
