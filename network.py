from dotenv import load_dotenv
import os
import json
import sys
import time
import networkx as nx
from IPython.display import display
import twitter
import pandas as pd
from urllib.error import URLError
from http.client import BadStatusLine
import nltk
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt 

load_dotenv()

OAUTH_TOKEN = os.environ.get("OAUTH_TOKEN")
OAUTH_TOKEN_SECRET = os.environ.get("OAUTH_TOKEN_SECRET")
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")

TWEETS_TO_ANALYZE = 100
SCREEN_NAME = "joerogan"

auth = twitter.oauth.OAuth(
    OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET
)

twitter_api = twitter.Twitter(auth=auth)

def save_to_pandas(data, fname):
    df = pd.DataFrame.from_records(data)
    df.to_pickle(fname)
    return df
    

def load_from_mongo(fname):
    df = pd.read_pickle(fname)
    return df

def twitter_search(twitter_api, q, max_results=200, **kw): ### Twitter Search Function that searches for tweets 

    # See https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets
    # and https://developer.twitter.com/en/docs/tweets/search/guides/standard-operators
    # for details on advanced search criteria that may be useful for 
    # keyword arguments
    
    # See https://dev.twitter.com/docs/api/1.1/get/search/tweets    
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
    
    for _ in range(10): # 10*100 = 1000
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError as e: # No more results when next_results doesn't exist
            break
            
        # Create a dictionary from next_results, which has the following form:
        # ?max_id=313519052523986943&q=NCAA&include_entities=1
        kwargs = dict([ kv.split('=') 
                        for kv in next_results[1:].split("&") ])
        
        search_results = twitter_api.search.tweets(**kwargs)
        statuses += search_results['statuses']
        
        if len(statuses) > max_results: 
            break
            
    return statuses

######################
    

# Sample usage

q = 'CrossFit'

results = twitter_search(twitter_api, q, max_results=10)

df = save_to_pandas(results, 'search_results_{}.pkl'.format(q))



tweets = []
for tweet in results:
    try:
        if tweet["retweet_count"] > 1:
            tweets.append(tweet)
    except:
        pass



# with open('your_file.txt', 'w') as f:
#     for item in tweets:
#         f.write("%s\n" % tweets)

zipped_result = []
for i, t in enumerate(tweets):
    # Extract the relevant portion of the tweet
    user = t["user"]["screen_name"]
    try:
        if 'retweeted_status' in t:
            retweetuser = t["retweeted_status"]["user"]["screen_name"],
            zipped_result.append(
    {
        "user": user,
        "retweetuser": retweetuser
    }
    )
    except:
        pass


final = json.dumps(zipped_result)
df1 = pd.read_json(final)
csv_file = df1.to_csv(f"data/test2.csv", index=None)

network = pd.DataFrame(zipped_result)

# print(user)

# network['retweetuser']=network['retweetuser'].str.replace('(','')
# print(network)

test = nx.from_pandas_edgelist(
    network,
    source = 'user',
    target = 'retweetuser',
    create_using = nx.DiGraph()
) 

print('Nodes in RT network:', len(test.nodes()))

# Create random layout positions
pos = nx.random_layout(test)

# Create size list
sizes = [x[1] for x in test.degree()]

# Draw the network
nx.draw_networkx(test, pos, 
    with_labels = False, 
    node_size = sizes,
    width = 0.1, alpha = 0.7,
    arrowsize = 2, linewidths = 0)

# Turn axis off and show
plt.axis('off'); plt.show(); plt.savefig('hi.png')




# Show some sample output, but just the user and text columns

#display(df)
#print('Nodes in RT network:', len(test.nodes()))
#csv_file = df.to_csv(f"data/test.csv", index=None)

 # 
# zipped_result = []
# for i, t in enumerate(results):
#     # Extract the text portion of the tweet
#     user = t["user"]["screen_name"]
#     retweetuser = t["retweeted_status"]["user"]["screen_name"]
#     zipped_result.append(
#     {
#         "user": user,
#         "retweetuser": retweetuser
#     }
#     )

# results1 = json.dumps(results)

# def flatten_tweets(results1):
#     tweets_list = []
#     for tweet in results1:
#         tweet_obj = json.loads(tweet)
#         # Store the user screen name in 'user-screen_name'
#         tweet_obj["user"] = tweet_obj["user"]["screen_name"]
    
#         if 'retweeted_status' in tweet_obj:
#          # Store the retweet user screen name in 'retweeted_status-user-screen_name'
#                 tweet_obj["retweetuser"] = tweet_obj["retweeted_status"]["user"]["screen_name"] 
#         tweets_list.append(tweet_obj)
#     return tweets_list 

# main = flatten_tweets(results1)

# df3 = pd.DataFrame(main)




    # if 'retweeted_status' in results:
    #     retweetuser = t["retweeted_status"]["screen_name"]
    #     zipped_result.append(
    #     {
    #         "user": user,
    #         "retweet_user": retweetuser
    #     }
    #     )




  
