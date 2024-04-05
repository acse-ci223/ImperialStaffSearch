# ImperialStaffSearch

## Overview
Academic Profile Scraper is a Python-based tool designed to extract and store faculty information from the Imperial webpage.

## Project Structure
- `src/`: The source directory containing the Python scripts.
  - `Database.py`: Handles database operations such as creating tables and inserting data.
  - `Profile.py`: Defines the `Profile` class responsible for fetching and storing profile data.
  - `Scraper.py`: Scrapes the URLs and manages the scraping process.
- `.env`: Directory containing environment files for virtual environments.
- `links.json`: JSON file containing the URLs to be scraped.
- `main.py`: The entry point of the application that orchestrates the scraping process.
- `profiles.db`: SQLite database where profile data is stored.
- `requirements.txt`: Lists all Python dependencies for the project.

## Installation
1. Clone the repository:

```shell
git clone https://github.com/acse-ci223/ImperialStaffSearch
```

2. Navigate to the project's root directory and set up a virtual environment:

```shell
python -m venv .venv
```

3. Activate the virtual environment and install dependencies:

```shell
source .venv/bin/activate # On Windows use .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage
Run `main.py` to start the scraping process:

```shell
python main.py
```


## Contributing
Contributions to this project are welcome. Please fork the repository and submit a pull request with your proposed changes.

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgements
- BeautifulSoup for HTML parsing.
- Requests for handling HTTP requests.

## Contact
For support or queries, please reach out to [maintainer-email].

---