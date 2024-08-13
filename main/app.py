import tweepy
from os import getenv
from time import sleep
from random import randint
import json
import schedule
import pytz
import datetime
import http.client

# Get credentials from environment variables
bearer_token = getenv('BEARER_TOKEN')
user_name_str = getenv('USER_NAME') #USER_NAME=elonmusk,123,456
rapid_provider_str = getenv('RAPID_PROVIDER')
reply_text_template = getenv('REPLY_TEXT')
rapid_key = getenv('RAPID_KEY')


client = tweepy.Client(bearer_token=bearer_token)

# List of user IDs you follow
followed_user_name = user_name_str.split(',') if user_name_str else []
rapid_provider = rapid_provider_str.split(',') if rapid_provider_str else []

# Store last tweet IDs
last_tweet_ids = {}

def rapid_get_tweets(provider,username):
    conn = http.client.HTTPSConnection(f"{provider}.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': rapid_key,
        'x-rapidapi-host': f"{provider}.p.rapidapi.com"
    }

    conn.request("GET", f"/timeline.php?screenname={username}", headers=headers)

    res = conn.getresponse()
    if res.status != 200:
        print(f"Error: Received status code {res.status}")
        return []
    
    data = res.read()

    # Parse the JSON data
    json_data = json.loads(data.decode("utf-8"))

    # Access the 'timeline' field and filter the data
    filtered_tweet_ids = [
        tweet['tweet_id'] 
        for tweet in json_data.get('timeline', [])
        if tweet.get('retweeted') is None
    ]

    # Print the tweet IDs
    return filtered_tweet_ids[:5]

def check_for_new_tweets():
    global last_tweet_ids
    for user in followed_user_name:
        tweets_ids = rapid_get_tweets('twitter-api45',user)
        for id in tweets_ids:
            if id not in last_tweet_ids.get(user, []):
                reply_text = f"{reply_text_template}"
                sleep(randint(5,9))
                client.create_tweet(in_reply_to_tweet_id=id, text=reply_text)
                last_tweet_ids.setdefault(user, []).append(id)
                last_tweet_ids[user] = last_tweet_ids[user][-8:] # keep the list of last 8 tweets


def schedule_mainland_time(hour, minute):
    mainland_tz = pytz.timezone('Asia/Shanghai')
    # Get current time in Mainland China timezone
    now = datetime.datetime.now(mainland_tz)
    print(now)
    # Calculate the next occurrence of the scheduled time
    schedule_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    # If the scheduled time is earlier in the day, adjust to the next day
    if now > schedule_time:
        schedule_time += datetime.timedelta(days=1)
    # Format the time for scheduling
    schedule.every().day.at(schedule_time.strftime('%H:%M')).do(check_for_new_tweets)

schedule_mainland_time(9, 0)  
schedule_mainland_time(12, 0)  
schedule_mainland_time(19, 30)

while True:
    schedule.run_pending()
    sleep(600)