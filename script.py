import os
import twitter
import json
import pymongo 
from dotenv import load_dotenv

load_dotenv()

OAUTH_TOKEN = os.environ.get("OAUTH_TOKEN")
OAUTH_TOKEN_SECRET = os.environ.get("OAUTH_TOKEN_SECRET")
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")

host = 'mongodb://localhost:27017'
q = 'Joe Rogan'

def oauth_login():
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

def twitter_search(twitter_api, q, max_results=200, **kw):
    search_results = twitter_api.search.tweets(q=q, count=100, **kw)

    statuses = search_results['statuses']

    # Iterate through batches of results by following the cursor until we
    # reach the desired number of results, keeping in mind that OAuth users
    # can "only" make 180 search queries per 15-minute interval. See
    # https://developer.twitter.com/en/docs/basics/rate-limits
    # for details. A reasonable number of results is ~1000, although
    # that number of results may not exist for all queries.

    # Enforce a reasonable limit
    max_results = min(1000, max_results)

    for _ in range(10):  # 10*100 = 1000
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError as e:  # No more results when next_results doesn't exist
            break

        # Create a dictionary from next_results, which has the following form:
        # ?max_id=313519052523986943&q=NCAA&include_entities=1
        kwargs = dict([kv.split('=')
                       for kv in next_results[1:].split("&")])

        search_results = twitter_api.search.tweets(**kwargs)
        statuses += search_results['statuses']

        if len(statuses) > max_results:
            break

    return statuses

def save_json(filename, data):
    with open('data/{0}.json'.format(filename),
              'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def load_json(filename):
    with open('data/{0}.json'.format(filename), 
              'r', encoding='utf-8') as f:
        return json.load(f)


# def save_to_mongo(data, mongo_db, mongo_db_coll, **mongo_conn_kw):

#     # Connects to the MongoDB server running on
#     # localhost:27017 by default

#     client = pymongo.MongoClient(**mongo_conn_kw)

#     # Get a reference to a particular database

#     db = client[mongo_db]

#     # Reference a particular collection in the database

#     coll = db[mongo_db_coll]

#     # Perform a bulk insert and  return the IDs
#     try:
#         return coll.insert_many(data)
#     except:
#         return coll.insert_one(data)


# def load_from_mongo(mongo_db, mongo_db_coll, return_cursor=False,
#                     criteria=None, projection=None, **mongo_conn_kw):

#     # Optionally, use criteria and projection to limit the data that is
#     # returned as documented in
#     # http://docs.mongodb.org/manual/reference/method/db.collection.find/

#     # Consider leveraging MongoDB's aggregations framework for more
#     # sophisticated queries.

#     client = pymongo.MongoClient(**mongo_conn_kw)
#     db = client[mongo_db]
#     coll = db[mongo_db_coll]

#     if criteria is None:
#         criteria = {}

#     if projection is None:
#         cursor = coll.find(criteria)
#     else:
#         cursor = coll.find(criteria, projection)

#     # Returning a cursor is recommended for large amounts of data

#     if return_cursor:
#         return cursor
#     else:
#         return [item for item in cursor]

twitter_api = oauth_login()
results = twitter_search(twitter_api, q, max_results=10)

print (results)

save_json(q, results)
results = load_json(q)

print(json.dumps(results, indent=1, ensure_ascii=False))

# ids = save_to_mongo(results, 'search_results', q, host=host)

# load_from_mongo('search_results', q, host=host)