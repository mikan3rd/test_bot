# coding: utf-8

import json
import re
from requests_oauthlib import OAuth1Session

import settings

twitter = OAuth1Session(
    settings.CONSUMER_KEY,
    settings.CONSUMER_SECRET,
    settings.ACCESS_TOKEN,
    settings.ACCESS_TOKEN_SECRET,
)


def get_account():
    endpoint = 'https://api.twitter.com/1.1/account/settings.json'
    response = twitter.get(endpoint)
    return json.loads(response.text)


def get_user_timeline(screen_name):
    endpoint = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    params = {
        'screen_name': screen_name,
    }
    response = twitter.get(endpoint, params=params)
    return json.loads(response.text)


def search_tweet(query):
    endpoint = "https://api.twitter.com/1.1/search/tweets.json"
    params = {
        'q': query,
        'count': 100,
    }
    response = twitter.get(endpoint, params=params)
    return json.loads(response.text).get('statuses')


def get_media_ids(tweets):
    media_ids = []

    for tweet in tweets:
        if tweet.get('quoted_status'):
            tweet = tweet['quoted_status']

        if tweet.get('entities').get('media'):
            media_list = tweet['entities']['media']
        else:
            media_list = tweet['entities']['urls']

        for media in media_list:
            media_ids.append(media.get("url"))

    return media_ids


def get_tweet_index(tweets, media_ids):
    tweet_index = 0

    for index, tweet in enumerate(tweets):
        if tweet.get('entities').get('media'):
            images = tweet['entities']['media']
        else:
            images = tweet['entities']['urls']

        for image in images:
            if image['url'] in media_ids:
                break

        else:
            tweet_index = index
            break

    return tweet_index


def create_tweet_content(tweet):
    screen_name = tweet['user']['screen_name']

    over_len = len(tweet['text']) - 120

    if over_len > 0:
        url_list = re.findall('https://t.co/.*', tweet['text'])
        tweet['text'] = tweet['text'][:-(over_len + len(url_list[-1]))]
        tweet['text'] += "... " + url_list[-1]

    tweet_list = []
    tweet_list.append("@" + screen_name + "\n")
    tweet_list.append(tweet['text'] + '\n')
    tweet_list.append(
        'ツイート元: https://twitter.com/' + screen_name +
        '/statuses/' + str(tweet['id'])
    )
    tweet_content = '\n'.join(tweet_list)
    return tweet_content


def post_tweet(tweet):
    endpoint = "https://api.twitter.com/1.1/statuses/update.json"
    params = {'status': tweet}
    response = twitter.post(endpoint, params=params)
    return json.loads(response.text)


def post_follow(user_id):
    endpoint = "https://api.twitter.com/1.1/friendships/create.json"
    params = {'user_id': user_id}
    return twitter.post(endpoint, params=params)


if __name__ == "__main__":
    # try:
    account = get_account()
    timeline_tweets = get_user_timeline(account['screen_name'])
    media_ids = get_media_ids(timeline_tweets)
    tweets = search_tweet('キズナアイ filter:images min_retweets:20')
    tweets = sorted(tweets, key=lambda k: k['retweet_count'], reverse=True)
    index = get_tweet_index(tweets, media_ids)
    tweet = tweets[index]
    tweet_content = create_tweet_content(tweet)
    print(tweet_content)
    post_follow(tweet['user']['id'])
    response = post_tweet(tweet_content)

    if response.get("errors"):
        print(response.get("errors"))

    print("SUCCESS!!")

    # except Exception as e:
    #     print("ERROR:", e)
