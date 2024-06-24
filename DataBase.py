import mysql.connector

class DataBase:

    def __init__(self, db_name):
        """
        Initialize the database connection and cursor.
        :param db_name: The name of the database.
        """
        self.db_name = db_name
        self.plug_and_play()

        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database=self.db_name
        )
        self.cursor = self.conn.cursor()

    def plug_and_play(self):
        # Build the database
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
        )
        mycursor = mydb.cursor()

        mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
        mycursor.execute(f"USE {self.db_name}")

        mycursor.execute(
            "CREATE TABLE IF NOT EXISTS users (username VARCHAR(255), password VARCHAR(255), port VARCHAR(255))"
        )

    def create_new_account(self, username, password, port):
        # Create a new account with the provided username, password, port

        try:
            query = "INSERT INTO users (username, password, port) VALUES (%s, %s, %s)"
            self.cursor.execute(query, (username, password, port))
            self.conn.commit()
            print(f"Account for {username} created successfully!")
        except mysql.connector.Error as e:
            print(f"Error creating a new account: {e}")

    def create_tables(self):
        # Create tables if they do not exist

        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username VARCHAR(255) PRIMARY KEY,
                    password VARCHAR(255),
                    port VARCHAR(255)
                )
            """)
            self.conn.commit()
            print("Table 'users' created successfully!")
        except mysql.connector.Error as e:
            print(f"Error creating tables: {e}")

    def is_username_in_database(self, username):
        # Check if the username is available (if someone already has this username)

        try:
            query = "SELECT * FROM users WHERE username=%s"
            self.cursor.execute(query, (username,))
            row = self.cursor.fetchone()
            return row is None  # if username exists return False
        except mysql.connector.Error as e:
            print(f"Error checking username availability: {e}")
            return False

    def find_username_info_database(self, username):
        # Find password and port (according to username) and return them if user is found
        try:
            query = "SELECT password, port FROM users WHERE username=%s"
            self.cursor.execute(query, (username,))
            row = self.cursor.fetchone()
            return row if row else None  # Return row if found, else None
        except mysql.connector.Error as e:
            print(f"Error finding password and port in database: {e}")
            return None
