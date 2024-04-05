import json
import requests
from bs4 import BeautifulSoup

__all__ = ['Scraper']


class Scraper:
    def __init__(self) -> None:
        with open('links.json', 'r') as file:
            self.__urls = json.load(file)["urls"]
        
    def __get_soup(self, url: str) -> BeautifulSoup:
        response = requests.get(url)
        return BeautifulSoup(response.text, 'html.parser')
    
    def __get_links(self, soup: BeautifulSoup) -> list:
        links = []
        for link in soup.find_all('a'):
            academic_url = link.get('href') or ''
            academic_url = academic_url.strip()
            if 'www.imperial.ac.uk/people/' in academic_url:
                academic_url = "https://www"+"".join(academic_url.split('www')[1:])
                links.append(academic_url)
        return links
    
    def scrape(self) -> list:
        profiles = []
        for url in self.__urls:
            soup = self.__get_soup(url)
            links = self.__get_links(soup)
            profiles.extend(links)
        profiles.sort()
        return profiles


if __name__ == "__main__":
    scraper = Scraper()
    profiles = scraper.scrape()
    print(*profiles, sep='\n')
