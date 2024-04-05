import requests
from bs4 import BeautifulSoup

__all__ = ['Profile']


class Profile:
    def __init__(self, url: str) -> None:
        self.__url = url
        self.__soup = self.__get_soup()
        self.__data = self.__get_main()
    
    def __get_soup(self) -> BeautifulSoup:
        """
        Returns the BeautifulSoup object for the profile URL.
        """
        response = requests.get(self.__url)
        return BeautifulSoup(response.text, 'html.parser')
    
    def __get_main(self) -> dict:
        """
        Extracts the main profile data from the page.
        """
        soup = self.__soup
        profile_data = {
            'name': 'N/A',
            'department': 'N/A',
            'contact': 'N/A',
            'location': 'N/A',
            'links': [],
            'summary': 'N/A',
            'publications': []
        }

        # Name extraction with redundancy
        try:
            name_parts = [soup.find(id=part_id).text.strip() for part_id in ['bannername', 'titlepart1', 'titlepart2', 'titlepart3'] if soup.find(id=part_id)]
            profile_data['name'] = ' '.join(name_parts) if name_parts else soup.find('h1').text.strip()
        except Exception as e:
            print(f"Error extracting name: {e}")

        # Department extraction with redundancy
        try:
            department_parts = [soup.find(id=part_id).text.strip() for part_id in ['titlepart4', 'titlepart5', 'department'] if soup.find(id=part_id)]
            profile_data['department'] = ', '.join(department_parts) if department_parts else soup.find(class_='department').text.strip()
        except Exception as e:
            print(f"Error extracting department: {e}")

        # Contact extraction with redundancy
        try:
            contact_email = soup.find('a', href=lambda x: x and 'mailto:' in x).get('href').replace('mailto:', '').strip()
            profile_data['contact'] = contact_email if contact_email else soup.find(text='Email').find_next('a').get('href').replace('mailto:', '').strip()
        except Exception as e:
            print(f"Error extracting contact: {e}")

        # Location extraction with redundancy
        try:
            location_parts = [soup.find(id=loc_id).text.strip() for loc_id in ['ot3', 'ot5', 'ot6', 'location'] if soup.find(id=loc_id)]
            profile_data['location'] = ', '.join(location_parts) if location_parts else soup.find(text='Location').find_next().text.strip()
        except Exception as e:
            print(f"Error extracting location: {e}")

        # Links extraction with redundancy
        try:
            profile_data['links'] = [a.get("href") for a in soup.select('ul.linklist a, .affiliations a')]
        except Exception as e:
            print(f"Error extracting links: {e}")

        # Summary extraction with redundancy
        try:
            summary_sections = soup.find('div', id='customContent').find_all('p') if soup.find('div', id='customContent') else soup.find_all('p', class_='summary')
            profile_data['summary'] = " ".join([p.text.strip() for p in summary_sections])
        except Exception as e:
            print(f"Error extracting summary: {e}")

        # Publications extraction with redundancy
        try:
            publications_list = soup.select('#latestPubsContainer .latestPubListing p, .publications .publication')
            profile_data['publications'] = [pub.text.strip() for pub in publications_list]
        except Exception as e:
            print(f"Error extracting publications: {e}")

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


