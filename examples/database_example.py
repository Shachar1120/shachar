import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="1234",
)
mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE IF NOT EXISTS mydatabase")
mycursor.execute("USE mydatabase")

mycursor.execute("CREATE TABLE IF NOT EXISTS users (username VARCHAR(255), password VARCHAR(255), port VARCHAR(255), channel_id INTEGER)")

sql = "INSERT INTO users (username, password, port, channel_id) VALUES (%s, %s, %s, %s)"
val = ("Shachar", "1234", "2001", 1)  # Note: port should be an integer
mycursor.execute(sql, val)

mydb.commit()

print(mycursor.rowcount, "record inserted.")
