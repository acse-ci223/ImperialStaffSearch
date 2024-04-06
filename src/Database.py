import sqlite3

from .Profile import Profile

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """
        Creates the profiles table if it doesn't exist.
        """
        self.cur.execute('''CREATE TABLE IF NOT EXISTS profiles (
                            name TEXT SECONDARY KEY,
                            url TEXT PRIMARY KEY,
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
    
    def get_profiles(self) -> list[Profile]:
        """
        Retrieves all profiles from the database.

        Returns
        -------
        list
            A list of Profile objects.
        """
        self.cur.execute('SELECT * FROM profiles WHERE contact IS NOT NULL')
        profiles = []
        for row in self.cur.fetchall():
            profile = Profile(row[1], name=row[0], department=row[2], contact=row[3], location=row[4], links=eval(row[5]), 
                              summary=row[6], publications=eval(row[7]))
            profiles.append(profile)
        return profiles

    def close(self):
        """
        Closes the database connection.
        """
        self.conn.close()


db = Database('profiles.db')


if __name__ == "__main__":
    db = Database('profiles.db')
    db.close()