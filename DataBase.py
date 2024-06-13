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
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
        )
        mycursor = mydb.cursor()

        mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
        mycursor.execute(f"USE {self.db_name}")

        mycursor.execute(
            "CREATE TABLE IF NOT EXISTS users (username VARCHAR(255), password VARCHAR(255), port VARCHAR(255), channel_id INTEGER)")

    def attempt_login(self, username, password):
        """
        Attempt to login with provided username and password.
        :param username: The username for login.
        :param password: The password for login.
        :return: The database row if login is successful, else None.
        """
        try:
            query = "SELECT * FROM users WHERE username=%s AND password=%s"
            self.cursor.execute(query, (username, password))
            row = self.cursor.fetchone()
            return row
        except mysql.connector.Error as e:
            print(f"Error during login: {e}")
            return None

    def is_username_available(self, username):
        """
        Check if the username is available.
        :param username: The username to check.
        :return: True if the username is available, else False.
        """
        try:
            query = "SELECT * FROM users WHERE username=%s"
            self.cursor.execute(query, (username,))
            row = self.cursor.fetchone()
            return row is None
        except mysql.connector.Error as e:
            print(f"Error checking username availability: {e}")
            return False

    def create_new_account(self, username, password, port, channel_id):
        """
        Create a new account with the provided username, password, port, and channel ID.
        :param username: The username for the new account.
        :param password: The password for the new account.
        :param port: The port associated with the new account.
        :param channel_id: The channel ID associated with the new account.
        """
        try:
            query = "INSERT INTO users (username, password, port, channel_id) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (username, password, port, channel_id))
            self.conn.commit()
            print(f"Account for {username} created successfully!")
        except mysql.connector.Error as e:
            print(f"Error creating a new account: {e}")

    def create_tables(self):
        """
        Create necessary tables if they do not exist.
        """
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username VARCHAR(255) PRIMARY KEY,
                    password VARCHAR(255),
                    port VARCHAR(255),
                    channel_id INTEGER
                )
            """)
            self.conn.commit()
            print("Table 'users' created successfully!")
        except mysql.connector.Error as e:
            print(f"Error creating tables: {e}")


def Main():

    ############## creating database

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
    )
    mycursor = mydb.cursor()

    mycursor.execute("CREATE DATABASE IF NOT EXISTS mydatabase")
    mycursor.execute("USE mydatabase")

    mycursor.execute(
        "CREATE TABLE IF NOT EXISTS users (username VARCHAR(255), password VARCHAR(255), port VARCHAR(255), channel_id INTEGER)")

    sql = "INSERT INTO users (username, password, port, channel_id) VALUES (%s, %s, %s, %s)"
    val = ("Shachar", "1234", "2001", 1)  # Note: port should be an integer
    mycursor.execute(sql, val)

    mydb.commit()

    print(mycursor.rowcount, "record inserted.")

    ##############

    # Initialize database connection
    db_name = "mydatabase"

    # Initialize the database object
    database_obj = DataBase(db_name)


    try:
        # Ensure tables are created if not exist
        database_obj.create_tables()

        username = "sss"
        password = "5555"
        port = "2001"
        channel_id = 1

        # Check if username is available
        if database_obj.is_username_available(username):
            # Create a new account
            database_obj.create_new_account(username, password, port, channel_id)
        else:
            print(f"Username {username} is already taken. Please choose another username.")

    except mysql.connector.Error as e:
        print(f"MySQL error: {e}")
    finally:
        # Close the database connection
        database_obj.conn.close()

if __name__ == "__main__":
    Main()
