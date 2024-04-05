
import logging
import concurrent.futures

from src.Scraper import Scraper
from src.Profile import Profile
from src.Database import Database
from src.WebUI import WebUI


def main():
    logging.info("Starting Staff Finder")
    ui = WebUI()
    logging.info("WebUI created")
    scraper = Scraper()
    logging.info("Scraper created")
    db = Database('profiles.db')
    logging.info("Database created")

    while True:
        urls = scraper.scrape()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            urls = [url for url in urls if not db.profile_exists(url)]
            future_to_url = {executor.submit(Profile, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    profile = future.result()
                    if not db.profile_exists(profile.url):
                        logging.info(f"Profile for {profile.get_data('name')} created")
                        db.insert_profile(profile)
                except Exception as exc:
                    logging.error(f"Profile for {url} failed to create")
                    logging.error(exc)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

if __name__ == "__main__":
    # logging.disable(logging.CRITICAL)
    main()