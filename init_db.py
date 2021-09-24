
import sqlite3

connection = sqlite3.connect('database.db')


with open('models/schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO books (title, author) VALUES (?, ?)",
            ('UnNamed', 'Unknown')
            )

cur.execute("INSERT INTO books (title, author) VALUES (?, ?)",
            ('NoName', 'You')
            )


connection.commit()
connection.close()