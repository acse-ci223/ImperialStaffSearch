# ImperialStaffSearch

## Overview

Staff Finder is a web application designed to streamline the process of searching for academic staff profiles based on research interests, departmental affiliations, or other keywords. This project consists of a backend written with FastAPI and a frontend built with Streamlit.

## Project Structure

The project is structured as follows:

- `src/`: The main source directory containing the Python modules.
  - `Database.py`: Module for database interactions.
  - `LoggerFormatter.py`: Custom logging formatter.
  - `Profile.py`: Profile data structure.
  - `Router.py`: FastAPI router handling the API routes.
  - `Scraper.py`: Web scraper for extracting staff information.
  - `SearchEngine.py`: Search functionality.
  - `WebUI.py`: Streamlit frontend interface.
- `.env`: Environment variables for configuration.
- `.gitignore`: Specifies intentionally untracked files to ignore.
- `backend.py`: Entry point for the FastAPI backend server.
- `frontend.py`: Entry point for the Streamlit frontend.
- `LICENSE`: License information for the project.
- `links.json`: Storage for scraped links.
- `profiles.db`: SQLite database for storing profile data.
- `README.md`: The file you are reading, containing documentation for the project.
- `requirements.txt`: List of dependencies to be installed.

## Installation

Before running the application, ensure you have Python installed and set up on your system.

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

To start the backend server, run:

```shell
python backend.py
```

To start the frontend server, run:

```shell
streamlit run frontend.py
```


## Contributing
Contributions to this project are welcome. Please fork the repository and submit a pull request with your proposed changes.

## License
Distributed under the MIT License. See `LICENSE` for more information.


## Contact
For support or queries, please create an issue.

---