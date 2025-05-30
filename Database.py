import mysql.connector

class Database:

    def __init__(self, _host, _user, _password, _database):  # <-- correct
        self.host = _host
        self.user = _user
        self.password = _password
        self.database = _database
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            print("Database connection established.")
            return True
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed.")

    def get_cursor(self):
        if self.cursor:
            return self.cursor
        else:
            print("Cursor is not initialized.")
            return None
