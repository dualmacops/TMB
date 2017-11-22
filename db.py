import sqlite3 as lite
import sys


class sql:
    def con(self):
        return lite.connect('bot.db')

    def categories(self):
        query = """ SELECT t1.name AS lev1, t2.name as lev2, t3.name as lev3
                    FROM category AS t1
                    LEFT JOIN category AS t2 ON t2.parent = t1.category_id
                    LEFT JOIN category AS t3 ON t3.parent = t2.category_id
                """
        with self.con()as con:
            cur = con.cursor()
            cur.execute(query)
            cur.close()
            con.commit()


    def SQLITE_VERSION(self):

        cur = self.con().cursor()

        cur.execute('SELECT SQLITE_VERSION()')
        data = cur.fetchone()
        cur.close()
        print("SQLite version: %s" % data)
        print(type(self.con()))

    def query_comit(self, text):
        with self.con()as con:
            cur = con.cursor()
            cur.execute(text)
            cur.close()
            con.commit()

    def query(self, text):
        with self.con()as con:
            cur = con.cursor()
            cur.execute(text)
            cur.close()

    def createTable(self):
        cur = self.con().cursor()
        with cur:
            pass
            # cur.execute("CREATE TABLE Cars(Id INT, Name TEXT, Price INT)")
            # cur.execute("INSERT INTO Cars VALUES(1,'Audi',52642)")
            # cur.execute("SELECT * FROM Cars;")


