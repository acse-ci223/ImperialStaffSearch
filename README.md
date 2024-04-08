# ImperialStaffSearch

Website running [here](http://iclstaff.com)

## Overview

Staff Finder is a web application designed to streamline the process of searching for academic staff profiles based on research interests, departmental affiliations, or other keywords. This project consists of a backend written with FastAPI and a frontend built with Streamlit.

## Features

- **Scraping** - The backend scrapes the Imperial College London website to retrieve staff profiles and their associated information.
- **Search** - Users can search for staff profiles based on keywords, research interests, or departmental affiliations.
  - **OpenAI Rank** - Generation of keywords to match relevancy in all profiles.
  - **TF-IDF Rank** - Using the Term Frequency-Inverse Document Frequency algorithm to rank search results.
  - **NLP Rank** - Using BERT embeddings to rank search results.

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