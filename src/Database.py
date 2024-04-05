import sqlite3

from .Profile import Profile

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """
        Creates the profiles table if it doesn't exist.
        """
        self.cur.execute('''CREATE TABLE IF NOT EXISTS profiles (
                            name TEXT PRIMARY KEY,
                            url TEXT SECONDARY KEY,
                            department TEXT,
                            contact TEXT,
                            location TEXT,
                            links TEXT,
                            summary TEXT,
                            publications TEXT
                        )''')
        self.conn.commit()

    def insert_profile(self, profile: Profile):
        """
        Inserts a profile into the database.

        Parameters
        ----------
        profile : Profile
            The Profile object to insert.
        """
        profile_data:dict = profile.get_data()
        self.cur.execute('''INSERT OR IGNORE INTO profiles (name, url, department, contact, location, links, summary, publications)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                         (profile_data['name'], profile.url, profile_data['department'], profile_data['contact'], 
                          profile_data['location'], str(profile_data['links']), profile_data['summary'], 
                          str(profile_data['publications'])))
        self.conn.commit()
    
    def profile_exists(self, url: str):
        """
        Checks if a profile exists in the database.

        Parameters
        ----------
        url : str
            The URL of the profile to check.

        Returns
        -------
        bool
            True if the profile exists, False otherwise.
        """
        self.cur.execute('SELECT * FROM profiles WHERE url=?', (url,))
        return self.cur.fetchone() is not None

    def close(self):
        """
        Closes the database connection.
        """
        self.conn.close()


if __name__ == "__main__":
    db = Database('profiles.db')
    db.close()