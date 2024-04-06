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
- `backend.Dockerfile`: Dockerfile for the backend server.
- `backend.py`: Entry point for the FastAPI backend server.
- `docker-compose.yml`: Docker Compose configuration for running the application.
- `frontend.Dockerfile`: Dockerfile for the frontend server.
- `frontend.py`: Entry point for the Streamlit frontend.
- `LICENSE`: License information for the project.
- `links.json`: Storage for scraped links.
- `profiles.db`: SQLite database for storing profile data.
- `README.md`: The file you are reading, containing documentation for the project.
- `requirements.txt`: List of dependencies to be installed.

## Installation

Before running the application, ensure you have Python and Docker installed and set up on your system.

- [Python Installation Guide](https://www.python.org/downloads/)
- [Docker Installation Guide](https://docs.docker.com/get-docker/)

1. Clone the repository:

```shell
git clone https://github.com/acse-ci223/ImperialStaffSearch
```

2. Navigate to the project's root directory and build the docker image:

```shell
cd ImperialStaffSearch
docker-compose build
```

## Usage

To start the frontend and backend server, run:

```shell
docker-compose up
```

The frontend should be accessible at `http://localhost:8501`, and the backend at `http://localhost:8000`.

## Contributing
Contributions to this project are welcome. Please fork the repository and submit a pull request with your proposed changes.

## License
Distributed under the MIT License. See `LICENSE` for more information.


## Contact
For support or queries, please create an issue.

---