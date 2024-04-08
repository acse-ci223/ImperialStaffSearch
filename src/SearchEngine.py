import asyncio
import logging
from typing import List

from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from scipy.spatial.distance import cosine as cosine_distance

from src.Profile import Profile
from src.Database import Database

class SearchEngine:
    def __init__(self, db: Database, open_ai_key: str):
        self.__db: Database = db  # The database instance for the engine instance
        self.__openai_key = open_ai_key
        self.__client = OpenAI(api_key=self.__openai_key)  # The OpenAI client for the engine instance
        self.__seed = 42
        # Initialize the TF-IDF vectorizer
        self.__vectorizer = TfidfVectorizer(stop_words='english')
        # Initialize the BERT model and tokenizer
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2').to(self.device)

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
                logging.error(f"Error while ranking profile: {profile.get_data('url')} - {e}")

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
        logging.info(f"Simple Ranking for: {query}")
        # Get the keywords from the query
        keywords = await self.__query_to_keywords(query)
        logging.info("Keywords: " + ", ".join(keywords))
        # Get the profiles from the database
        profiles = await self.__db.get_profiles()
        # Rank the profiles by the keywords
        ranked_profiles = await self.__rank_by_keywords(profiles, keywords)
        # Return the top n profiles
        return ranked_profiles[:top_n]
    
    async def __compute_tfidf_matrix(self, documents: List[str]):
        """
        Asynchronously compute the TF-IDF matrix for a list of documents.
        """
        loop = asyncio.get_event_loop()
        tfidf_matrix = await loop.run_in_executor(None, lambda: self.__vectorizer.fit_transform(documents))
        return tfidf_matrix

    async def __compute_query_vector(self, query: str):
        """
        Asynchronously compute the TF-IDF vector for a search query.
        """
        loop = asyncio.get_event_loop()
        query_vector = await loop.run_in_executor(None, lambda: self.__vectorizer.transform([query]))
        return query_vector
    
    async def __tf_idf_rank(self, query: str, top_n: int = 25) -> List[Profile]:
        """
        This function ranks profiles based on the cosine similarity between the query and the profile text.

        Parameters
        ----------
        query : str
            The query to search for.
        top_n : int
            The number of profiles to return.
        
        Returns
        -------
        List[Profile]
            A list of profiles ranked by the cosine similarity between the query and the profile text.
        """
        logging.info(f"TF-IDF Ranking for: {query}")
        profiles = await self.__db.get_profiles()

        # Prepare documents for TF-IDF computation
        documents = [str(profile) for profile in profiles]  # Assuming each profile has a 'summary' attribute

        # Compute TF-IDF matrix for documents
        tfidf_matrix = await self.__compute_tfidf_matrix(documents)

        # Compute TF-IDF vector for query
        query_vector = await self.__compute_query_vector(query)

        # Compute cosine similarity between query vector and document matrix
        cosine_similarities = await asyncio.get_event_loop().run_in_executor(
            None, lambda: cosine_similarity(query_vector, tfidf_matrix).flatten()
        )

        # Get indices of profiles sorted by similarity
        sorted_indices = np.argsort(cosine_similarities)[::-1]

        # Select top N profiles
        top_profile_indices = sorted_indices[:top_n]

        # Return the top N profiles
        top_profiles = [profiles[index] for index in top_profile_indices]
        return top_profiles
    
    async def __embed_text(self, text: str) -> torch.Tensor:
        """
        Asynchronously generate embeddings for a given piece of text.
        """
        loop = asyncio.get_event_loop()
        encoded_input = self.tokenizer(text, padding=True, truncation=True, max_length=128, return_tensors='pt').to(self.device)
        with torch.no_grad():
            model_output = await loop.run_in_executor(None, lambda: self.model(**encoded_input))
        embeddings = model_output.last_hidden_state.mean(dim=1)
        return embeddings

    async def __calculate_similarity(self, query_embedding: np.ndarray, profile_embedding: np.ndarray) -> float:
        try:
            cosine_sim = 1 - cosine_distance(query_embedding, profile_embedding)  # Use NumPy arrays for calculation
            return cosine_sim
        except Exception as e:
            logging.error(f"Error while calculating similarity: {e}")
            return -1
    
    async def __bert_rank(self, query: str, top_n: int = 25) -> List[Profile]:
        logging.info(f"BERT Ranking for: {query}")

        # Get all profiles from the database
        profiles = await self.__db.get_profiles()
        
        # Embed the query
        query_embedding = await self.__embed_text(query)
        query_embedding = query_embedding.detach().cpu().numpy().flatten()  # Ensure detachment, move to CPU, and flatten

        # Create tasks for embedding all profile summaries
        profile_embedding_tasks = [self.__embed_text(profile.get_data("summary")) for profile in profiles]
        profile_embeddings = await asyncio.gather(*profile_embedding_tasks)

        # Detach and move embeddings to CPU, then flatten
        profile_embeddings = [embedding.detach().cpu().numpy().flatten() for embedding in profile_embeddings]

        # Calculate similarity scores in parallel
        similarity_scores_tasks = [self.__calculate_similarity(query_embedding, profile_embedding) for profile_embedding in profile_embeddings]
        similarity_scores = await asyncio.gather(*similarity_scores_tasks)

        # Associate profiles with their similarity scores
        profile_similarity_scores = list(zip(profiles, similarity_scores))

        # Sort profiles by similarity score
        profile_similarity_scores.sort(key=lambda x: x[1], reverse=True)

        # Select top N profiles
        top_profiles = [profile for profile, _ in profile_similarity_scores[:top_n]]
        return top_profiles

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
        # Simple ranking based on keywords - OpenAI
        ranked_profiles = await self.__simple_rank(query, top_n)

        # TF-IDF ranking
        ranked_profiles = await self.__tf_idf_rank(query, top_n)

        # BERT ranking
        ranked_profiles = await self.__bert_rank(query, top_n)

        # Can add more complex ranking functions here
        
        return ranked_profiles
