import sqlite3


# Creating database
conn = sqlite3.connect("Cash_Logger2.db")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS User (
          ID INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT,
          password TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS Expenses (
          ID INTEGER PRIMARY KEY AUTOINCREMENT,
          User_ID INTEGER,
          Date TEXT,
          Amount INTEGER,
          Category TEXT,
          Description TEXT,
          FOREIGN KEY (User_ID) REFERENCES User(ID))""")
c.execute("""CREATE TABLE IF NOT EXISTS INCOME (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                User_ID INTEGER,
                Amount INTEGER ,
                Source TEXT ,
                Date TEXT ,
                FOREIGN KEY (User_ID) REFERENCES User(ID))""")
conn.commit()
conn.close()