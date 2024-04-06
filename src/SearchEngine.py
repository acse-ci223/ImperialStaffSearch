import logging

import openai
from openai import OpenAI

from src.Profile import Profile
from src.Database import Database

class SearchEngine:
    def __init__(self, db: Database, open_ai_key: str):
        self.__db: Database = db
        self.__openai_key = open_ai_key
        self.__client = OpenAI(api_key=self.__openai_key)
        self.__seed = 42
        logging.info("Search Engine initialized")

    def __query_to_keywords(self, query: str) -> list[str]:
        try:
            response = self.__client.chat.completions.create(
                model="gpt-3.5-turbo-16k-0613",
                seed=self.__seed,
                temperature=1.2,
                max_tokens=50,
                top_p=1.0,
                frequency_penalty=0.2,
                presence_penalty=0.2,
                messages=[
                    {"role": "system",
                     "content": "Understand the topic of the query and generate 50 relevant keywords in a comma-separated list."},
                    {"role": "user",
                     "content": query}
                ]
            )
            content = response.choices[0].message.content
            keywords: list[str] = content.split(', ')
            keywords = [keyword.strip() for keyword in keywords if keyword.strip()]
            return keywords
        except openai.OpenAIError as e:
            logging.error(f"Error with OpenAI API: {e}")
            return []
    
    def __rank_by_keywords(self, profiles: list[Profile], keywords: list[str]) -> list[Profile]:
        ranked_list = []
        for profile in profiles:
            string: str = str(profile)
            keyword_count = sum(keyword.lower() in string.lower() for keyword in keywords)
            ranked_list.append((profile, keyword_count))
        ranked_list.sort(key=lambda x: x[1], reverse=True)
        ranked_list: list[Profile] = [x[0] for x in ranked_list]
        return ranked_list
    
    def __simple_rank(self,  query: str, top_n: int = 10) -> list[Profile]:
        keywords = self.__query_to_keywords(query)
        logging.info("Keywords: " + ", ".join(keywords))
        profiles = self.__db.get_profiles()
        logging.info("Profiles: " + str(len(profiles)))
        ranked_list = self.__rank_by_keywords(profiles, keywords)
        return ranked_list[:top_n]
    
    def __openai_rank(self, query: str, profiles: list[Profile]) -> list[Profile]:
        inst = """
        Sort the following profiles based on their relevance to the given query.
        Return a list of json objects with the following structure:
        {
            'sorted_profiles':[
                {
                    'name': The name of the profile,
                    'department': The department of the profile,
                    'contact': The contact information of the profile,
                    'location': The location of the profile,
                    'links': The links array associated with the profile,
                    'summary': The summary of the profile,
                    'publications': The publications array associated with the profile,
                    'url': The url of the profile
                }
            ]
        }
        """
        msg = f"Query: {query}\n\n"
        for i, profile in enumerate(profiles):
            msg += f"{i+1}. {str(profile.to_dict())}\n"

        try:
            response = self.__client.chat.completions.create(
                model="gpt-4-0125-preview",
                seed=self.__seed,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": inst},
                    {"role": "user", "content": msg}
                ]
            )
            res = eval(response.choices[0].message.content)
            return res['sorted_profiles']
        except openai.OpenAIError as e:
            logging.error(f"Error with OpenAI API: {e}")
        return []

    def search(self, query: str, top_n: int = 25, extensive: bool= False) -> list[Profile]:
        logging.info("Searching for: " + str(query))
        ranked_profiles: list[Profile] = self.__simple_rank(query, top_n)
        if extensive:
            ranked_profiles: list[Profile] = self.__openai_rank(query, ranked_profiles)
        return ranked_profiles
