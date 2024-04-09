# External imports
import sqlite3
import asyncio

# Internal imports
from .Profile import Profile

class Database:
    def __init__(self, db_name: str = 'profiles.db'):
        self.db_name = db_name  # Database filename
        self.loop = asyncio.get_event_loop()  # Get the current event loop to use asynchronously in the class

    async def create_table(self):
        """
        Asynchronously creates the profiles table if it doesn't exist.
        """
        await self.loop.run_in_executor(None, self._sync_create_table)

    def _sync_create_table(self):
        """Creates the profiles table if it doesn't exist."""
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

    async def update_profile(self, profile: Profile):
        """
        Asynchronously updates a profile in the database.
        """
        await self.loop.run_in_executor(None, self._sync_update_profile, profile)

    def _sync_update_profile(self, profile: Profile):
        """Updates a profile in the database."""
        profile_data = profile.to_dict()
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute('''UPDATE profiles SET name=?, department=?, contact=?, location=?, links=?, summary=?, publications=?
                            WHERE url=?''',
                        (profile_data['name'], profile_data['department'], profile_data['contact'], profile_data['location'],
                         str(profile_data['links']), profile_data['summary'], str(profile_data['publications']), profile_data['url']))
            conn.commit()

    async def insert_profile(self, profile: Profile):
        """
        Asynchronously inserts a profile into the database.
        """
        await self.loop.run_in_executor(None, self._sync_insert_profile, profile)

    def _sync_insert_profile(self, profile: Profile):
        """Inserts a profile into the database."""
        profile_data = profile.to_dict()
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
        Asynchronously checks if a profile exists in the database.
        """
        return await self.loop.run_in_executor(None, self._sync_profile_exists, url)

    def _sync_profile_exists(self, url: str) -> bool:
        """Checks if a profile exists in the database."""
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM profiles WHERE url=?', (url,))
            return cur.fetchone() is not None

    async def get_profiles(self) -> list[Profile]:
        """
        Asynchronously retrieves all profiles from the database.
        """
        return await self.loop.run_in_executor(None, self._sync_get_profiles)

    def _sync_get_profiles(self) -> list[Profile]:
        """Retrieves all profiles from the database."""
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            # query = '''
            # SELECT * FROM profiles
            # WHERE name != 'N/A' AND
            #     department != 'N/A'
            # '''
            # cur.execute(query)
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
        """
        Asynchronously fetches existing URLs from the database.
        """
        loop = asyncio.get_running_loop()  # Get the current event loop. Sometimes the loop is not the same as the class loop
        existing_urls = await loop.run_in_executor(None, self._sync_fetch_existing_urls)
        return existing_urls
    
    def _sync_fetch_existing_urls(self) -> list[str]:
        """Fetches existing URLs from the database."""
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            query = '''
            SELECT url FROM profiles
            WHERE name != 'N/A' AND
                department != 'N/A' AND
                contact != 'N/A' AND
                location != 'N/A' AND
                summary != 'N/A'
            '''
            cur.execute(query)
            return [row[0] for row in cur.fetchall()]  # Return a list of URLs. row[0] is the URL from cur.fetchall()
    
    async def fetch_profile(self, url: str) -> Profile:
        """
        Asynchronously fetches a profile from the database.
        """
        return await self.loop.run_in_executor(None, self._sync_fetch_profile, url)
    
    def _sync_fetch_profile(self, url: str) -> Profile:
        """Fetches a profile from the database."""
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM profiles WHERE url=?', (url,))
            row = cur.fetchone()
            if row:
                profile_data = {
                    'name': row[0],
                    'department': row[2],
                    'contact': row[3],
                    'location': row[4],
                    'links': eval(row[5]),
                    'summary': row[6],
                    'publications': eval(row[7])
                }
                return Profile(url=row[1], **profile_data)
            return Profile(url=url)


if __name__ == "__main__":
    db = Database('profiles.db')
    db.create_table()