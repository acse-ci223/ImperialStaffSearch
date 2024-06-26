import json
import httpx
from bs4 import BeautifulSoup

__all__ = ['Scraper']


class Scraper:
    def __init__(self) -> None:
        try:
            with open('links.json', 'r') as file:
                self.__urls = json.load(file)["urls"]

        except FileNotFoundError:
            self.__urls = []
        
    async def __get_soup(self, url: str) -> BeautifulSoup:
        """
        Returns a BeautifulSoup object from the given URL.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        return BeautifulSoup(response.text, 'html.parser')
    
    def __get_links(self, soup: BeautifulSoup) -> list:
        """
        Returns a list of academic profile URLs from the given BeautifulSoup object.
        """
        links = []
        for link in soup.find_all('a'):
            try:
                # Get the URL from the 'href' attribute
                academic_url = link.get('href') or ''
                academic_url = academic_url.strip()
                if 'www.imperial.ac.uk/people/' in academic_url:
                    # Fix the URL if it doesn't start with 'https://www'
                    academic_url = "https://www"+"".join(academic_url.split('www')[1:])
                    links.append(academic_url)

            except Exception:
                pass

        return links
    
    async def scrape(self) -> list:
        """
        Returns a list of academic profile URLs.
        """
        profiles = []
        async with httpx.AsyncClient() as client:
            for url in self.__urls:
                try:
                    # Get the BeautifulSoup object from the URL
                    soup = await self.__get_soup(url)
                    links = self.__get_links(soup)
                    profiles.extend(links)
                
                except Exception:
                    pass

        profiles.sort()
        return profiles


if __name__ == "__main__":
    import asyncio
    
    async def main():
        scraper = Scraper()
        profiles = await scraper.scrape()
        print(*profiles, sep='\n')

    asyncio.run(main())
