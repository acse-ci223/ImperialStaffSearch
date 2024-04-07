import sqlite3
import asyncio

from .Profile import Profile

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.loop = asyncio.get_event_loop()

    async def create_table(self):
        """
        Creates the profiles table if it doesn't exist.
        """
        await self.loop.run_in_executor(None, self._sync_create_table)

    def _sync_create_table(self):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS profiles (
                            name TEXT SECONDARY KEY,
                            url TEXT PRIMARY KEY,
                            department TEXT,
                            contact TEXT,
                            location TEXT,
                            links TEXT,
                            summary TEXT,
                            publications TEXT
                        )''')
            conn.commit()

    async def insert_profile(self, profile: Profile):
        """
        Inserts a profile into the database.
        """
        await self.loop.run_in_executor(None, self._sync_insert_profile, profile)

    def _sync_insert_profile(self, profile: Profile):
        profile_data = profile.to_dict()  # Assuming Profile.to_dict() is synchronous and safe to call
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute('''INSERT OR IGNORE INTO profiles (name, url, department, contact, location, links, summary, publications)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (profile_data['name'], profile_data['url'], profile_data['department'], profile_data['contact'],
                         profile_data['location'], str(profile_data['links']), profile_data['summary'],
                         str(profile_data['publications'])))
            conn.commit()

    async def profile_exists(self, url: str) -> bool:
        """
        Checks if a profile exists in the database.
        """
        return await self.loop.run_in_executor(None, self._sync_profile_exists, url)

    def _sync_profile_exists(self, url: str) -> bool:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM profiles WHERE url=?', (url,))
            return cur.fetchone() is not None

    async def get_profiles(self) -> list[Profile]:
        """
        Retrieves all profiles from the database.
        """
        return await self.loop.run_in_executor(None, self._sync_get_profiles)

    def _sync_get_profiles(self) -> list[Profile]:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM profiles')
            profiles = []
            for row in cur.fetchall():
                profile_data = {
                    'name': row[0],
                    'department': row[2],
                    'contact': row[3],
                    'location': row[4],
                    'links': eval(row[5]),
                    'summary': row[6],
                    'publications': eval(row[7])
                }
                profile = Profile(url=row[1], **profile_data)
                profiles.append(profile)
            return profiles
    
    async def fetch_existing_urls(self) -> list[str]:
        loop = asyncio.get_running_loop()
        existing_urls = await loop.run_in_executor(None, db._sync_fetch_existing_urls)
        return existing_urls
    
    def _sync_fetch_existing_urls(self) -> list[str]:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute('SELECT url FROM profiles')
            return [row[0] for row in cur.fetchall()]

    def close(self):
        """
        Closes the database connection.
        """
        self.conn.close()


if __name__ == "__main__":
    db = Database('profiles.db')
    db.close()