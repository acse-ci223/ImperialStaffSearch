import asyncio
import logging
from typing import List

import openai
from openai import OpenAI

from src.Profile import Profile
from src.Database import Database

class SearchEngine:
    def __init__(self, db: Database, open_ai_key: str):
        self.__db: Database = db  # The database instance for the engine instance
        self.__openai_key = open_ai_key
        self.__client = OpenAI(api_key=self.__openai_key)  # The OpenAI client for the engine instance
        self.__seed = 42
        logging.info("Async Search Engine initialized")

    async def __query_to_keywords(self, query: str, recursive: int = 0, recursive_max: int= 3) -> list[str]:
        """
        This function takes a query and returns a list of keywords that are relevant to the query.

        Parameters
        ----------
        query : str
            The query to convert to keywords.
        recursive : int
            The number of recursive calls made to the OpenAI API.
        recursive_max : int
            The maximum number of recursive calls to make to the OpenAI API.
        
        Returns
        -------
        list[str]
            A list of keywords that are relevant to the query.
        """
        # Recursive call to the OpenAI API to get keywords from the query
        if recursive > recursive_max:
            return []
        try:
            # Run in executor needs to be called with the current event loop
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, lambda: self.__client.chat.completions.create(
                model="gpt-3.5-turbo-16k-0613",  # gpt-3.5-turbo-16k-0613 is fast and returns good results
                seed=self.__seed,
                temperature=1.2,
                max_tokens=50,
                top_p=1.0,
                frequency_penalty=0.2,
                presence_penalty=0.2,
                messages=[
                    # This message returns a list of keywords based on the query
                    {"role": "system",
                     "content": "Understand the topic of the query and generate 50 relevant keywords in a comma-separated list."},
                    {"role": "user",
                     "content": query}
                ]
            ))
            # Extract the keywords from the response
            if response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content
                keywords = [keyword.strip() for keyword in content.split(',') if keyword.strip()]
                return keywords
            else:
                logging.error("Unexpected response format from OpenAI API.")
                return await self.__query_to_keywords(query, recursive=recursive + 1)
        except Exception as e:
            logging.error(f"Error with OpenAI API: {e}")
            return []

    async def __rank_by_keywords(self, profiles: List[Profile], keywords: List[str]) -> List[Profile]:
        """
        This function ranks the profiles based on the number of keywords found in the profile text.

        Parameters
        ----------
        profiles : List[Profile]
            The list of profiles to rank.
        keywords : List[str]
            The list of keywords to rank the profiles by.
        
        Returns
        -------
        List[Profile]
            A list of profiles ranked by the number of keywords found in the profile text.
        """
        ranked_profiles = []
        # Set the keyword count for each profile
        for profile in profiles:
            try:
                profile_text = str(profile)
                keyword_count = sum(keyword.lower() in profile_text.lower() for keyword in keywords)
                ranked_profiles.append((profile, keyword_count))
            except Exception as e:
                logging.error(f"Error while ranking profile: {profile.get_data("url")} - {e}")

        # Sort the profiles by the number of keywords found in the profile text
        # Sorting in descending order on the second index of the tuple
        ranked_profiles.sort(key=lambda x: x[1], reverse=True)
        # Return just the profiles
        return [profile for profile, _ in ranked_profiles]

    async def __simple_rank(self, query: str, top_n: int = 10) -> List[Profile]:
        """
        This is a simple ranking function that ranks profiles based on the number of keywords found in the profile text.

        Parameters
        ----------
        query : str
            The query to search for.
        top_n : int
            The number of profiles to return.

        Returns
        -------
        List[Profile]
            A list of profiles ranked by the number of keywords found in the profile text.
        """
        # Get the keywords from the query
        keywords = await self.__query_to_keywords(query)
        logging.info("Keywords: " + ", ".join(keywords))
        # Get the profiles from the database
        profiles = await self.__db.get_profiles()
        logging.info(f"Found {len(profiles)} profiles")
        # Rank the profiles by the keywords
        ranked_profiles = await self.__rank_by_keywords(profiles, keywords)
        # Return the top n profiles
        return ranked_profiles[:top_n]
    
    async def search(self, query: str, top_n: int = 25) -> List[Profile]:
        """
        This function searches for profiles based on a query.

        Parameters
        ----------
        query : str
            The query to search for.
        top_n : int
            The number of profiles to return.
        
        Returns
        -------
        List[Profile]
            A list of profiles ranked by the number of keywords found in the profile text.
        """
        logging.info(f"Searching for: {query}")
        # Simple ranking based on keywords
        ranked_profiles = await self.__simple_rank(query, top_n)

        # Can add more complex ranking functions here
        
        return ranked_profiles
