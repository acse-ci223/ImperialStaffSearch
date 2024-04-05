import concurrent.futures
from src.Scraper import Scraper
from src.Profile import Profile
from src.Database import Database


def main():
    scraper = Scraper()
    urls = scraper.scrape()
    db = Database('profiles.db')

    # Use ThreadPoolExecutor to parallelize profile creation
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Map each URL to the Profile constructor, creating profiles in parallel
        future_to_url = {executor.submit(Profile, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                profile = future.result()
                print(f"Profile for {profile.get_data('name')} created")
                db.insert_profile(profile.get_data())
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))


if __name__ == "__main__":
    main()