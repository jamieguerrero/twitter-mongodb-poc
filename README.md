## Getting Started

To run this script, you must have an .env file with the following keys:
- CONSUMER_KEY
- CONSUMER_SECRET
- OAUTH_TOKEN
- OAUTH_TOKEN_SECRET

You will also need python (pyenv) and mongodb running.

- install pyenv
- install python (v3.9.2 at the time of development)

- create virtualenv `python -m venv .venv`

- start venv
Windows: `.venv\Scripts\activate.bat`
Mac/Linux: `source .venv/bin/activate`

- pip install requirements
`pip install -r requirements.txt`

- create a folder called `data` in the root directory
- run script with `python script.py`
