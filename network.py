from dotenv import load_dotenv
import os
import json
import networkx as nx
import twitter
import pandas as pd
from urllib.error import URLError
from http.client import BadStatusLine
import matplotlib.pyplot as plt 

load_dotenv()

#Auth stuff 

OAUTH_TOKEN = os.environ.get("OAUTH_TOKEN")
OAUTH_TOKEN_SECRET = os.environ.get("OAUTH_TOKEN_SECRET")
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")

auth = twitter.oauth.OAuth(
    OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET
)

twitter_api = twitter.Twitter(auth=auth)

### Twitter Search Function that searches for tweets 
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
    

#Enter search here 

q = 'yosakoi'

results = twitter_search(twitter_api, q, max_results=10)

#Flatten tweets
zipped_result = []
for i, t in enumerate(results):
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

network = pd.DataFrame(zipped_result) #Create df 

#Use nx to create the network using an edgelist with 2 columns
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
    with_labels = True, 
    node_size = sizes,
    width = 0.1, alpha = 0.7,
    arrowsize = 2, linewidths = 0)

# Turn axis off and show
plt.axis('off'); plt.show(); plt.savefig('hi.png')

# Generate in-degree centrality for retweets 
rt_centrality = nx.in_degree_centrality(test)

column_names = ['screen_name', 'degree_centrality']

# Store centralities in DataFrame
rt = pd.DataFrame(list(rt_centrality.items()), columns = column_names)

# Print first five results in descending order of centrality
print(rt.sort_values('degree_centrality', ascending = False).head())

###################

# Generate betweenness centrality for retweets 
rt_centrality = nx.betweenness_centrality(test)

column_names = ['screen_name', 'betweenness_centrality']
# Store centralities in data frames
rt = pd.DataFrame(list(rt_centrality.items()), columns = column_names)

# Print first five results in descending order of centrality
print(rt.sort_values('betweenness_centrality', ascending = False).head())




