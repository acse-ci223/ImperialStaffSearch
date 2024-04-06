import asyncio
import logging
from typing import List

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
        logging.info("Async Search Engine initialized")

    async def __query_to_keywords(self, query: str) -> list[str]:
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, lambda: self.__client.chat.completions.create(
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
            ))
            if response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content
                keywords = [keyword.strip() for keyword in content.split(',') if keyword.strip()]
                return keywords
            else:
                logging.error("Unexpected response format from OpenAI API.")
                return []
        except Exception as e:
            logging.error(f"Error with OpenAI API: {e}")
            return []

    async def __rank_by_keywords(self, profiles: List[Profile], keywords: List[str]) -> List[Profile]:
        ranked_profiles = []
        for profile in profiles:
            profile_text = str(profile)
            keyword_count = sum(keyword.lower() in profile_text.lower() for keyword in keywords)
            ranked_profiles.append((profile, keyword_count))
        ranked_profiles.sort(key=lambda x: x[1], reverse=True)
        return [profile for profile, _ in ranked_profiles]

    async def __simple_rank(self, query: str, top_n: int = 10) -> List[Profile]:
        keywords = await self.__query_to_keywords(query)
        logging.info("Keywords: " + ", ".join(keywords))
        profiles = await self.__db.get_profiles()
        logging.info(f"Found {len(profiles)} profiles")
        ranked_profiles = await self.__rank_by_keywords(profiles, keywords)
        return ranked_profiles[:top_n]
    
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
    
    async def search(self, query: str, top_n: int = 25) -> List[Profile]:
        logging.info(f"Searching for: {query}")
        ranked_profiles = await self.__simple_rank(query, top_n)
        return ranked_profiles
