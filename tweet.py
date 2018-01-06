# coding: utf-8

import json
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

        if not tweet.get('extended_entities'):
            tweet = tweet['quoted_status']

        media_list = tweet.get('extended_entities').get('media')
        for media in media_list:
            media_ids.append(media.get("id"))

    return media_ids


def get_tweet_index(tweets, media_ids):
    tweet_index = 0

    for index, tweet in enumerate(tweets):
        images = tweet['extended_entities']['media']

        for image in images:
            if image['id'] in media_ids:
                break

        else:
            tweet_index = index
            break

    return tweet_index


def create_tweet_content(tweet):
    screen_name = tweet['user']['screen_name']
    tweet_list = []
    tweet_list.append(
        str(tweet['retweet_count']) + "RT @" + screen_name + "\n")
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
    return twitter.post(endpoint, params=params)


def post_follow(user_id):
    endpoint = "https://api.twitter.com/1.1/friendships/create.json"
    params = {'user_id': user_id}
    return twitter.post(endpoint, params=params)


if __name__ == "__main__":
    # try:
    account = get_account()
    timeline_tweets = search_tweet(account['screen_name'])
    media_ids = get_media_ids(timeline_tweets)
    tweets = search_tweet('キズナアイ filter:images min_retweets:20')
    tweets = sorted(tweets, key=lambda k: k['retweet_count'], reverse=True)

    # for tweet in tweets:
    #     print("RT:", tweet['retweet_count'])

    index = get_tweet_index(tweets, media_ids)
    tweet = tweets[index]
    tweet_content = create_tweet_content(tweet)
    print(tweet_content)
    post_follow(tweet['user']['id'])
    post_tweet(tweet_content)
    print("SUCCESS!!")

    # except Exception as e:
    #     print("ERROR:", e)
