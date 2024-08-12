import tweepy
import os
import time

# Get credentials from environment variables
consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
user_id_str = os.getenv('USER_ID') #USER_ID=123456,789012,345678
reply_text_template = os.getenv('REPLY_TEXT')

# Authentication
auth = tweepy.OAuth1UserHandler(consumer_key, 
                                consumer_secret,
                                access_token,
                                access_token_secret)
api = tweepy.API(auth)

# List of user IDs you follow
followed_users = user_id_str.split(',') if user_id_str else []


# Store last tweet IDs
last_tweet_ids = {}

def check_for_new_tweets():
    global last_tweet_ids
    for user_id in followed_users:
        tweets = api.user_timeline(user_id=user_id, count=1)
        for tweet in tweets:
            if tweet.id not in last_tweet_ids.get(user_id, []):
                reply_text = f"{reply_text_template}"
                api.update_status(status=reply_text, in_reply_to_status_id=tweet.id)
                last_tweet_ids.setdefault(user_id, []).append(tweet.id)

while True:
    check_for_new_tweets()
    time.sleep(600)  # Sleep for 10 minutes