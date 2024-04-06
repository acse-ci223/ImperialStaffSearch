import asyncio
import logging
import concurrent.futures
from enum import Enum
import threading

from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.Scraper import Scraper
from src.Profile import Profile
from src.Database import db, Database
from src.LoggerFormatter import CustomFormatter
from src.Router import Router

import dotenv
dotenv.load_dotenv(override=True)

class AppMode(str, Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"

APP_MODE = AppMode.STOPPED


def start_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scrape_and_update())
    loop.close()

async def scrape_and_update(delay: int = 10):
    scraper = Scraper()  # Assuming scraper is now an async class
    db = Database("profiles.db")
    await db.create_table()
    while APP_MODE == AppMode.RUNNING:
        logging.info("Scraping profiles")
        
        # Scrape URLs asynchronously
        urls = await scraper.scrape()
        logging.info(f"Scraped {len(urls)} URLs")
        
        # Fetch existing URLs from the database asynchronously
        existing_urls = await db.fetch_existing_urls()
        logging.info(f"Found {len(existing_urls)} existing profiles")
        
        tasks = []
        for url in urls:
            if url not in existing_urls:
                logging.info(f"Creating task for {url}")
                task = asyncio.create_task(create_and_save_profile(url))
                tasks.append(task)
        
        await asyncio.gather(*tasks)
        logging.info("Finished scraping profiles")
        logging.info(f"Waiting {delay} seconds")
        await asyncio.sleep(delay)

async def create_and_save_profile(url: str):
    try:
        logging.info(f"Creating profile for {url}")
        # Create a Profile instance asynchronously
        profile: Profile = await Profile.create(url)
        
        # Insert the profile into the database asynchronously
        await db.insert_profile(profile)  
        logging.info(f"Profile for {profile.get_data('name')} created")
    except Exception as exc:
        logging.warning(f"Profile creation failed for {url}")
        logging.error(exc)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up")
    global APP_MODE
    APP_MODE = AppMode.RUNNING
    
    # Create and start a new thread for scrape_and_update
    scrape_thread = threading.Thread(target=lambda: asyncio.run(start_async_loop()), daemon=True)
    scrape_thread.start()
    
    yield
    
    APP_MODE = AppMode.STOPPED
    logging.info("Waiting for the scraping thread to finish")
    scrape_thread.join()  # Wait for the scrape_and_update thread to finish if it's still running
    logging.info("Shutting down")


logging.basicConfig(level=logging.INFO)
logging.getLogger().handlers[0].setFormatter(CustomFormatter())

app = FastAPI(lifespan=lifespan)
app.include_router(Router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
