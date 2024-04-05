import os
import logging
import dotenv

from fastapi import APIRouter
from pydantic import BaseModel

from src.SearchEngine import SearchEngine
from .Database import db

dotenv.load_dotenv(override=True)

class ProfileRequest(BaseModel):
    query: str


__all__ = ["Router"]

Router = APIRouter()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@Router.post("/profiles")
async def get_profiles(req: ProfileRequest) -> dict:
    global db
    logging.info("POST /profiles")
    try:
        engine = SearchEngine(db=db, open_ai_key=OPENAI_API_KEY)
        response = engine.search(req.query)
        profiles = [profile.to_dict() for profile in response]
        return {"profiles": profiles, "code": 200}
    except Exception as e:
        logging.error(e)
        return {"error": e, "code": 500}
    

@Router.get("/ping")
async def ping() -> dict:
    logging.info("GET /ping")
    return {"message": "pong", "code": 200}
