import sqlite3

import requests

from gethoney.models import Honeypot

# TODO: Make dynamic list with table names in initiation


class Database:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.curr = self.conn.cursor()
        self.curr.execute(
            """CREATE TABLE IF NOT EXISTS honeypots
        (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT, description TEXT)"""
        )
        self.curr.execute(
            """CREATE TABLE IF NOT EXISTS logs
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT,
              honeypot_id INTEGER,
              FOREIGN KEY (honeypot_id) REFERENCES honeypots (id))"""
        )

    def insert_into_db(self, honeypots: list[Honeypot]):
        self.curr.executemany(
            """INSERT INTO honeypots
                        (name, url, description)
                        VALUES (?, ?, ?) """,
            [(honeypot.name, honeypot.url, honeypot.description) for honeypot in honeypots],
        )

        self.conn.commit()

        # TODO: Return exactly what's being inserted into DB, which includes auto incremented ID
        # self.curr.execute(
        #     """SELECT id FROM honeypots WHERE
        #             (name) == VALUES (?) """,
        #     (honeypots[0].name),
        # )
        # data = self.curr.fetchall()
        # return data

    # TODO: Make Select * dynamic from list in initiator

    def select_from_db(self):
        data = self.curr.execute("SELECT * FROM honeypots").fetchall()
        return data

    def retrieve_logs(self, honeypot: Honeypot):

        fetch_url_id = self.curr.execute("SELECT url, id FROM honeypots WHERE name == ?", (honeypot.name,)).fetchall()

        url = fetch_url_id[0][0]
        id = fetch_url_id[0][1]

        request = requests.get(url)
        data = request.json()

        self.curr.executemany(
            """INSERT INTO logs
            (name, honeypot_id)
            VALUES (?, ?)""",
            [(item["name"], id) for item in data],
        )
        self.conn.commit()

    def update_honeypot(self, honeypot: Honeypot, _id: int):
        params = [honeypot.name, honeypot.url, honeypot.description, _id]

        self.curr.execute("UPDATE honeypots SET name = ?, url = ?, description = ? WHERE id == ?", (params))
        self.conn.commit()

    def delete_honeypot(self, _id: int):

        self.curr.execute(
            """DELETE FROM honeypots
            WHERE id == ?""",
            (_id,),
        )
        self.conn.commit()

    def get_honeypot(self, _id: int):
        data = self.curr.execute("SELECT * FROM honeypots WHERE id == ?", (_id,)).fetchall()
        return data


# Random Test Code

# gethoney_db = "../data/gethoney.db"
# f = Database(gethoney_db)
# hp = Honeypot(name="bob", url="http://1.1.1.1", description=" ")
