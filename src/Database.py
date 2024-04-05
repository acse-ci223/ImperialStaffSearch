import sqlite3

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS profiles (
                            name TEXT PRIMARY KEY,
                            department TEXT,
                            contact TEXT,
                            location TEXT,
                            links TEXT,
                            summary TEXT,
                            publications TEXT
                        )''')
        self.conn.commit()

    def insert_profile(self, profile_data):
        self.cur.execute('''INSERT OR IGNORE INTO profiles (name, department, contact, location, links, summary, publications)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                         (profile_data['name'], profile_data['department'], profile_data['contact'], 
                          profile_data['location'], str(profile_data['links']), profile_data['summary'], 
                          str(profile_data['publications'])))
        self.conn.commit()

    def close(self):
        self.conn.close()