
from src.Scraper import Scraper


def main():
    scraper = Scraper()
    profiles = scraper.scrape()
    print(*profiles, sep='\n')


if __name__ == "__main__":
    main()