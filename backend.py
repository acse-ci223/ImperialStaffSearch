import asyncio
import logging
import concurrent.futures
from enum import Enum

from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.Scraper import Scraper
from src.Profile import Profile
from src.Database import db
from src.LoggerFormatter import CustomFormatter
from src.Router import Router

import dotenv
dotenv.load_dotenv(override=True)

class AppMode(str, Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"

scraper = Scraper()
APP_MODE = AppMode.STOPPED

async def scrape_and_update():
    while APP_MODE == AppMode.RUNNING:
        logging.info("Scraping profiles")
        urls = scraper.scrape()
        logging.info(f"Scraped {len(urls)} profiles")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            urls = [url for url in urls]
            logging.info(f"Creating profiles for {len(urls)} urls")
            future_to_url = {executor.submit(Profile, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                if APP_MODE != AppMode.RUNNING:
                    break
                url = future_to_url[future]
                try:
                    profile = future.result()
                    if not db.profile_exists(profile.url):
                        logging.info(f"Profile for {profile.get_data('name')} created")
                        db.insert_profile(profile)
                    else:
                        logging.warning(f"Profile for {profile.get_data('name')} already exists")
                except Exception as exc:
                    logging.error(f"Profile for {url} failed to create")
                    logging.error(exc)
        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up")
    global APP_MODE
    APP_MODE = AppMode.RUNNING
    asyncio.create_task(scrape_and_update())
    yield
    APP_MODE = AppMode.STOPPED
    logging.info("Shutting down")


logging.basicConfig(level=logging.INFO)
logging.getLogger().handlers[0].setFormatter(CustomFormatter())

app = FastAPI(lifespan=lifespan)
app.include_router(Router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
