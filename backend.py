# Internal imports
import asyncio
import logging
from enum import Enum
import threading
import traceback

# External imports
from fastapi import FastAPI
from contextlib import asynccontextmanager
import dotenv

# Local imports
from src.Scraper import Scraper
from src.Profile import Profile
from src.Database import Database
from src.LoggerFormatter import CustomFormatter
from src.Router import Router

dotenv.load_dotenv(override=True)

class AppMode(str, Enum):  # Enum for the application mode
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"

APP_MODE = AppMode.STOPPED

# Function to start the asynchronous loop that scrapes and updates profiles
def start_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scrape_and_update())
    loop.close()

async def scrape_and_update(delay: int = 60):
    # Create a Scraper and Database instance
    scraper = Scraper()
    db = Database("profiles.db")
    await db.create_table() # Create the table if it doesn't exist

    while APP_MODE == AppMode.RUNNING:
        logging.info("Scraping profiles")
        try:
            # Scrape URLs asynchronously
            urls = await scraper.scrape()
            logging.info(f"Scraped {len(urls)} URLs")
            
            # Fetch existing URLs from the database asynchronously
            db = Database("profiles.db")
            existing_urls = await db.fetch_existing_urls()
            logging.info(f"Found {len(existing_urls)} existing profiles")
            
            # Create tasks for new URLs asynchronously
            tasks = []
            for url in urls:
                if url not in existing_urls:
                    logging.info(f"Creating task for {url}")
                    task = asyncio.create_task(create_and_save_profile(url))
                    tasks.append(task)
                else:
                    logging.warning(f"Updating profile for {url}")
                    task = asyncio.create_task(update_profile(url))
                    tasks.append(task)
            
            # Wait for all tasks to finish
            await asyncio.gather(*tasks)
            logging.info("Finished scraping profiles")
            logging.info(f"Waiting {delay} seconds")
        except Exception as exc:
            tb = traceback.format_exc()
            logging.error(f"An error occurred: {exc}\nTraceback: {tb}")
        # Wait for the specified delay
        await asyncio.sleep(delay)

async def update_profile(url: str):
    try:
        logging.info(f"Updating profile for {url}")
        # Create a Profile instance asynchronously
        profile: Profile = await Profile.create(url)
        db_profile: Profile = await Database().fetch_profile(url)
        if len(str(profile)) > len(str(db_profile)):
            # Update the profile in the database asynchronously
            await Database().update_profile(profile)  
            logging.info(f"Profile for {profile.get_data('name')} updated")

    except Exception as exc:
        logging.warning(f"Profile update failed for {url}")
        logging.error(exc)

async def create_and_save_profile(url: str):
    try:
        logging.info(f"Creating profile for {url}")
        # Create a Profile instance asynchronously
        profile: Profile = await Profile.create(url)
        
        # Insert the profile into the database asynchronously
        db = Database()
        await db.insert_profile(profile)  
        logging.info(f"Profile for {profile.get_data('name')} created")

    except Exception as exc:
        logging.warning(f"Profile creation failed for {url}")
        logging.error(exc)

# Asynchronous context manager for the application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up")
    global APP_MODE
    APP_MODE = AppMode.RUNNING
    
    # Create and start a new thread for scrape_and_update
    scrape_thread = threading.Thread(target=lambda: asyncio.run(start_async_loop()), daemon=True)
    scrape_thread.start()
    
    # Return control to the FastAPI app
    yield
    
    APP_MODE = AppMode.STOPPED
    logging.info("Waiting for the scraping thread to finish")
    scrape_thread.join()  # Wait for the scrape_and_update thread to finish if it's still running
    logging.info("Shutting down")

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger().handlers[0].setFormatter(CustomFormatter())

# Create a FastAPI instance
app = FastAPI(lifespan=lifespan)
app.include_router(Router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
