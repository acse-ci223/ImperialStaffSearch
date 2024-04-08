# Internal imports
import os
import logging

# External imports
from fastapi import APIRouter
from pydantic import BaseModel

# Local imports
import dotenv
from .SearchEngine import SearchEngine
from .Database import Database

dotenv.load_dotenv(override=True)

# Model for the profile request
class ProfileRequest(BaseModel):
    query: str # The query to search for


__all__ = ["Router"]

Router = APIRouter()  # The router for the API. Accessed in backend.py

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@Router.post("/profiles/long")  # The endpoint for getting profiles
async def get_profiles(req: ProfileRequest) -> dict:
    """
    Returns the profiles for the specified query.

    Parameters
    ----------
    req : ProfileRequest
        The request containing the query.

    Returns
    -------
    dict
        The profiles for the specified query.
    """
    logging.info("POST /profiles/long")
    try:
        db = Database()
        # Create a search engine instance
        engine = SearchEngine(db=db, open_ai_key=OPENAI_API_KEY)
        response = await engine.long_search(req.query)
        # Convert the profiles to dictionaries to become serialized
        profiles = [profile.to_dict() for profile in response]
        return {"profiles": profiles, "code": 200}

    except Exception as e:
        logging.error(e)
        return {"error": e, "code": 500}
    
@Router.post("/profiles/quick")  # The endpoint for getting profiles
async def get_profiles(req: ProfileRequest) -> dict:
    """
    Returns the profiles for the specified query.

    Parameters
    ----------
    req : ProfileRequest
        The request containing the query.

    Returns
    -------
    dict
        The profiles for the specified query.
    """
    logging.info("POST /profiles/quick")
    try:
        db = Database()
        # Create a search engine instance
        engine = SearchEngine(db=db, open_ai_key=OPENAI_API_KEY)
        response = await engine.quick_search(req.query)
        # Convert the profiles to dictionaries to become serialized
        profiles = [profile.to_dict() for profile in response]
        return {"profiles": profiles, "code": 200}

    except Exception as e:
        logging.error(e)
        return {"error": e, "code": 500}
    
@Router.post("/profiles/norm")  # The endpoint for getting profiles
async def get_profiles(req: ProfileRequest) -> dict:
    """
    Returns the profiles for the specified query.

    Parameters
    ----------
    req : ProfileRequest
        The request containing the query.

    Returns
    -------
    dict
        The profiles for the specified query.
    """
    logging.info("POST /profiles/norm")
    try:
        db = Database()
        # Create a search engine instance
        engine = SearchEngine(db=db, open_ai_key=OPENAI_API_KEY)
        response = await engine.search(req.query)
        # Convert the profiles to dictionaries to become serialized
        profiles = [profile.to_dict() for profile in response]
        return {"profiles": profiles, "code": 200}

    except Exception as e:
        logging.error(e)
        return {"error": e, "code": 500}
    

@Router.get("/ping")
async def ping() -> dict:
    logging.info("GET /ping")
    return {"message": "pong", "code": 200}
