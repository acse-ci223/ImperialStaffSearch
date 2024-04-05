import logging

from fastapi import APIRouter
from pydantic import BaseModel

from src.SearchEngine import SearchEngine
from .Database import db

__all__ = ["Router"]


class ProfileRequest(BaseModel):
    query: str


Router = APIRouter()


@Router.post("/profiles")
async def get_profiles(req: ProfileRequest) -> dict:
    global db
    logging.info("POST /profiles")
    try:
        engine = SearchEngine(db=db, open_ai_key="")
        response = engine.search(req.query)
        return {"profiles": [profile.to_dict() for profile in response]}
    except Exception as e:
        logging.error(e)
        return {"error": 404}


@Router.get("/stop_scraping")
async def stop_scraping() -> dict:
    logging.info("GET /stop_scraping")
    return {"error": 404}
