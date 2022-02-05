## Getting Started

To run this app, you must have an .env file with the following keys:
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
Mac: `source .venv/bin/activate`

- pip install requirements
`pip install -r requirements.txt`

- start mongo
i have these aliases in my `~/.zshrc` (or `~/.bashrc`) file 

```
alias startmongo='brew services start mongodb-community'
alias stopmongo='brew services stop mongodb-community'
alias startmongobg='mongod --config /usr/local/etc/mongod.conf'
alias stopmongobd='mongo admin --eval "db.shutdownServer()"'
```

- open mongodb compass
- run script with `python script.py`