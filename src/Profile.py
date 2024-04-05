import logging

import requests
from bs4 import BeautifulSoup

__all__ = ['Profile']


class Profile:
    def __init__(self, url: str, **profile_data) -> None:
        self.url = url
        self.__data = {
            'name': 'N/A',
            'department': 'N/A',
            'contact': 'N/A',
            'location': 'N/A',
            'links': [],
            'summary': 'N/A',
            'publications': [],
            'url': url
        }
        if len(profile_data) == 0:
            self.__soup = self.__get_soup()
            self.__data = self.__get_main()
        else:
            self.set_data(**profile_data)
    
    def __get_soup(self) -> BeautifulSoup:
        """
        Returns the BeautifulSoup object for the profile URL.
        """
        response = requests.get(self.url)
        return BeautifulSoup(response.text, 'html.parser')
    
    def __get_main(self) -> dict:
        soup = self.__soup
        profile_data = {
            'name': 'N/A',
            'department': 'N/A',
            'contact': 'N/A',
            'location': 'N/A',
            'links': [],
            'summary': 'N/A',
            'publications': [],
            'url': self.url
        }

        # Name extraction with redundancy
        try:
            name_parts = [soup.find(id=part_id).text.strip() for part_id in ['bannername', 'titlepart1', 'titlepart2', 'titlepart3'] if soup.find(id=part_id)]
            profile_data['name'] = ' '.join(name_parts) if name_parts else soup.find('h1').text.strip()
        except Exception as e:
            try:
                profile_data['name'] = soup.find(class_='profile-name').text.strip()
            except Exception as e:
                logging.error(f"Error extracting name: {e}")

        # Department extraction with redundancy
        try:
            department_parts = [soup.find(id=part_id).text.strip() for part_id in ['titlepart4', 'titlepart5'] if soup.find(id=part_id)]
            profile_data['department'] = ', '.join(department_parts) if department_parts else soup.find(class_='department-info').text.strip()
        except Exception as e:
            logging.error(f"Error extracting department: {e}")

        # Contact extraction with redundancy
        try:
            profile_data['contact'] = soup.select_one('a[href^="mailto:"]').get('href').replace('mailto:', '').strip()
        except Exception as e:
            try:
                profile_data['contact'] = soup.find(class_='contact-email').text.strip()
            except Exception as e:
                logging.error(f"Error extracting contact: {e}")

        # Location extraction with redundancy
        try:
            location_parts = [soup.find(id=loc_id).text.strip() for loc_id in ['ot3', 'ot5', 'ot6'] if soup.find(id=loc_id)]
            profile_data['location'] = ', '.join(location_parts) if location_parts else soup.find(class_='location-info').text.strip()
        except Exception as e:
            logging.error(f"Error extracting location: {e}")

        # Links extraction with redundancy
        try:
            profile_data['links'] = [a.get("href") for a in soup.select('ul.linklist a')]
        except Exception as e:
            try:
                profile_data['links'] = [a.get("href") for a in soup.select('.affiliations a')]
            except Exception as e:
                logging.error(f"Error extracting links: {e}")

        # Summary extraction with redundancy
        try:
            summary_sections = soup.select('#customContent p')
            profile_data['summary'] = " ".join([p.text.strip() for p in summary_sections])
        except Exception as e:
            try:
                profile_data['summary'] = soup.find(class_='summary-text').text.strip()
            except Exception as e:
                logging.error(f"Error extracting summary: {e}")

        # Publications extraction with redundancy
        try:
            publications_list = soup.select('#latestPubsContainer .latestPubListing p')
            profile_data['publications'] = [pub.text.strip() for pub in publications_list]
        except Exception as e:
            try:
                profile_data['publications'] = [pub.text.strip() for pub in soup.select('.publications-listing p')]
            except Exception as e:
                logging.error(f"Error extracting publications: {e}")

        return profile_data

    def get_data(self, *args) -> dict:
        """
        Returns the profile data as a dictionary. If arguments are passed, only the specified keys are returned.
        """
        if args:
            data = {key: self.__data[key] for key in args}
            if len(data) == 1:
                return data.popitem()[1]
            return data
        return self.__data

    def set_data(self, **kwargs) -> None:
        """
        Sets the profile data with the specified key-value pairs.
        """
        for key, value in kwargs.items():
            if key in self.__data:
                self.__data[key] = value
            else:
                logging.error(f"Key '{key}' does not exist in profile data")
        
    def to_dict(self) -> dict:
        """
        Returns the profile data as a dictionary.
        """
        return self.__data    

    def __str__(self) -> str:
        profile_str: str = f"Name: {self.__data['name']}, "
        profile_str += f"Department: {self.__data['department']}, "
        profile_str += f"Contact: {self.__data['contact']}, "
        profile_str += f"Location: {self.__data['location']}, "
        profile_str += f"Links: {', '.join(self.__data['links'])}, "
        profile_str += f"Summary: {self.__data['summary']}, "
        profile_str += f"Publications: {', '.join(self.__data['publications'])}"
        return profile_str
    
    def __repr__(self) -> str:
        return self.__str__()
