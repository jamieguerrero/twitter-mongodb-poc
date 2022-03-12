import os
import twitter
import json
import pandas as pd
import nltk
import pymongo 
from dotenv import load_dotenv
# pip install nltk

nltk.download('vader_lexicon')

import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer

load_dotenv()

OAUTH_TOKEN = os.environ.get("OAUTH_TOKEN")
OAUTH_TOKEN_SECRET = os.environ.get("OAUTH_TOKEN_SECRET")
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")

TWEETS_TO_ANALYZE = 100

auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                           CONSUMER_KEY, CONSUMER_SECRET)

twitter_api = twitter.Twitter(auth=auth)


##############################################################

import sys
import time
from urllib.error import URLError
from http.client import BadStatusLine
import json
import twitter

def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw): 
    
    # A nested helper function that handles common HTTPErrors. Return an updated
    # value for wait_period if the problem is a 500 level error. Block until the
    # rate limit is reset if it's a rate limiting issue (429 error). Returns None
    # for 401 and 404 errors, which requires special handling by the caller.
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
    
        if wait_period > 3600: # Seconds
            print('Too many retries. Quitting.', file=sys.stderr)
            raise e
    
        # See https://developer.twitter.com/en/docs/basics/response-codes
        # for common codes
    
        if e.e.code == 401:
            print('Encountered 401 Error (Not Authorized)', file=sys.stderr)
            return None
        elif e.e.code == 404:
            print('Encountered 404 Error (Not Found)', file=sys.stderr)
            return None
        elif e.e.code == 429: 
            print('Encountered 429 Error (Rate Limit Exceeded)', file=sys.stderr)
            if sleep_when_rate_limited:
                print("Retrying in 15 minutes...ZzZ...", file=sys.stderr)
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print('...ZzZ...Awake now and trying again.', file=sys.stderr)
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print('Encountered {0} Error. Retrying in {1} seconds'\
                  .format(e.e.code, wait_period), file=sys.stderr)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

    # End of nested helper function
    
    wait_period = 2 
    error_count = 0 

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError as e:
            error_count = 0 
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError as e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print("URLError encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise
        except BadStatusLine as e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print("BadStatusLine encountered. Continuing.", file=sys.stderr)
            if error_count > max_errors:
                print("Too many consecutive errors...bailing out.", file=sys.stderr)
                raise



###############################################################

def harvest_user_timeline(twitter_api, screen_name=None, user_id=None, max_results=1000):
     
    assert (screen_name != None) != (user_id != None), \
    "Must have screen_name or user_id, but not both"    
    
    kw = {  # Keyword args for the Twitter API call
        'count': TWEETS_TO_ANALYZE,
        'trim_user': 'true',
        'include_rts' : 'true',
        'since_id' : 1
        }
    
    if screen_name:
        kw['screen_name'] = screen_name
    else:
        kw['user_id'] = user_id
        
    max_pages = 16
    results = []
    
    tweets = make_twitter_request(twitter_api.statuses.user_timeline, **kw)
    
    if tweets is None: # 401 (Not Authorized) - Need to bail out on loop entry
        tweets = []
        
    results += tweets
    
    print('Fetched {0} tweets'.format(len(tweets)), file=sys.stderr)
    
    page_num = 1
    
    # Many Twitter accounts have fewer than 200 tweets so you don't want to enter
    # the loop and waste a precious request if max_results = 200.
    
    # Note: Analogous optimizations could be applied inside the loop to try and 
    # save requests. e.g. Don't make a third request if you have 287 tweets out of 
    # a possible 400 tweets after your second request. Twitter does do some 
    # post-filtering on censored and deleted tweets out of batches of 'count', though,
    # so you can't strictly check for the number of results being 200. You might get
    # back 198, for example, and still have many more tweets to go. If you have the
    # total number of tweets for an account (by GET /users/lookup/), then you could 
    # simply use this value as a guide.
    
    if max_results == kw['count']:
        page_num = max_pages # Prevent loop entry
    
    while page_num < max_pages and len(tweets) > 0 and len(results) < max_results:
    
        # Necessary for traversing the timeline in Twitter's v1.1 API:
        # get the next query's max-id parameter to pass in.
        # See https://dev.twitter.com/docs/working-with-timelines.
        kw['max_id'] = min([ tweet['id'] for tweet in tweets]) - 1 
    
        tweets = make_twitter_request(twitter_api.statuses.user_timeline, **kw)
        results += tweets

        print('Fetched {0} tweets'.format(len(tweets)),file=sys.stderr)
    
        page_num += 1
        
    print('Done fetching tweets', file=sys.stderr)

    return results[:max_results]
    
# Sample usage

ptweets = harvest_user_timeline(twitter_api, screen_name="joerogan", \
                               max_results=TWEETS_TO_ANALYZE)

# Save to MongoDB with save_to_mongo or a local file with save_json...

###############################################################




twitter_stream = twitter.TwitterStream(auth=auth)
iterator = twitter_stream.statuses.sample()
tweets = []
for tweet in ptweets:
    try:
        if tweet['lang'] == 'en':
            tweets.append(tweet)
    except:
        pass
    if len(tweets) == TWEETS_TO_ANALYZE:
        break
analyzer = SentimentIntensityAnalyzer()
analyzer.polarity_scores('Hello')
analyzer.polarity_scores('I really enjoy this video series.')
analyzer.polarity_scores('I REALLY enjoy this video series.')
analyzer.polarity_scores('I REALLY enjoy this video series!!!')
analyzer.polarity_scores('I REALLY did not enjoy this video series!!!')
scores = np.zeros(len(tweets))

zipped_result = []

for i, t in enumerate(tweets):
    # Extract the text portion of the tweet
    text = t['text']
    created_at = t['created_at']
    retweet_count = t['retweet_count']
    # Measure the polarity of the tweet
    polarity = analyzer.polarity_scores(text)
    
    # Store the normalized, weighted composite score
    scores[i] = polarity['compound']
    zipped_result.append({
    "score": polarity['compound'],
    "tweet": text,
    "created_at": created_at,
    "retweed_count": retweet_count

    })
most_positive = np.argmax(scores)
most_negative = np.argmin(scores)
# print('{0:6.3f} : "{1}"'.format(scores[most_positive], tweets[most_positive]['text']))
# print('{0:6.3f} : "{1}"'.format(scores[most_negative], tweets[most_negative]['text']))
# print(scores)
# print(tweets)

# def zip_up_results(scores, tweets):
#     zipped_up_array = []
#     for index in range(len(scores)):
#         score = scores[i]
#         tweet = tweets[i]
#         print(tweet.data)

#         zipped_up_array.append({
#             "score": score,
#             "date": tweet.created_at,
#             "text": tweet.text,
#             "retweets": tweet.entity.retweets
#         })
#     return zipped_up_array
# print(zip_up_results(scores, tweets))

def save_json(filename, data):
    with open('data/{0}.json'.format(filename),
              'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def load_json(filename):
    with open('data/{0}.json'.format(filename), 
              'r', encoding='utf-8') as f:
        return json.load(f)

print(zipped_result)
final = json.dumps(zipped_result)
df = pd.read_json (final)
csv_file = df.to_csv (r'Rogan.csv', index = None)

