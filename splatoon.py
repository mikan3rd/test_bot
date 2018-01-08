# coding: utf-8

import json
import re
from requests_oauthlib import OAuth1Session

import settings

twitter = OAuth1Session(
    settings.CONSUMER_KEY_SPLATOON,
    settings.CONSUMER_SECRET_SPLATOON,
    settings.ACCESS_TOKEN_SPLATOON,
    settings.ACCESS_TOKEN_SECRET_SPLATOON,
)


def get_account():
    endpoint = 'https://api.twitter.com/1.1/account/settings.json'
    response = twitter.get(endpoint)
    return json.loads(response.text)


def get_user_timeline(screen_name):
    endpoint = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    params = {
        'screen_name': screen_name,
        'count': 200,
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


def post_tweet(
    tweet,
    in_reply_to_status_id=None,
):
    endpoint = "https://api.twitter.com/1.1/statuses/update.json"
    params = {'status': tweet}

    if in_reply_to_status_id:
        params['in_reply_to_status_id'] = in_reply_to_status_id

    response = twitter.post(endpoint, params=params)
    return json.loads(response.text)


def post_follow(user_id):
    endpoint = "https://api.twitter.com/1.1/friendships/create.json"
    params = {'user_id': user_id}
    response = twitter.post(endpoint, params=params)
    return json.loads(response.text)


def get_user_followers(screen_name):
    endpoint = "https://api.twitter.com/1.1/followers/list.json"
    params = {'screen_name': screen_name}
    response = twitter.get(endpoint, params=params)
    return json.loads(response.text).get('users')


def get_retweeters(id):
    endpoint = "https://api.twitter.com/1.1/statuses/retweets/" + \
        str(id) + ".json"
    params = {
        'trim_user': False,
    }
    response = twitter.get(endpoint, params=params)
    return json.loads(response.text)


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
        url_list = re.findall('https://t.co/\S*', tweet['text'])
        tweet['text'] = tweet['text'][:-(over_len + len(url_list[-1]))]
        tweet['text'] += "... " + url_list[-1]
        tweet['text'] = re.sub('(http|#|@)\S*\.\.\.', '...', tweet['text'])

    tweet_list = []
    tweet_list.append(tweet['text'] + '\n')
    tweet_list.append("ツイート元: @" + screen_name)
    tweet_list.append(
        'https://twitter.com/' + screen_name +
        '/statuses/' + str(tweet['id'])
    )
    tweet_content = '\n'.join(tweet_list)
    return tweet_content


def get_not_follow_ids(users):
    ids = []

    for user in users:
        if user.get('following') is False:
            ids.append(user['id'])

    return ids


if __name__ == "__main__":
    # try:
    account = get_account()
    timeline_tweets = get_user_timeline(account['screen_name'])
    media_ids = get_media_ids(timeline_tweets)
    tweets = search_tweet(
        '#Splatoon2 filter:videos min_retweets:50')
    tweets = sorted(tweets, key=lambda k: k['retweet_count'], reverse=True)
    index = get_tweet_index(tweets, media_ids)
    tweet = tweets[index]
    tweet_content = create_tweet_content(tweet)
    print(tweet_content)
    response = post_tweet(
        tweet_content,
        in_reply_to_status_id=tweet['id'],
    )

    if response.get("errors"):
        print(response.get("errors"))

    tweet_ids = []
    for timeline_tweet in timeline_tweets:
        if timeline_tweet['retweet_count'] > 0:
            tweet_ids.append(timeline_tweet['id'])

    retweeter_list = []
    for tweet_id in tweet_ids:
        retweet_list = get_retweeters(tweet_id)
        for retweet in retweet_list:
            retweeter_list.append(retweet['user'])

    followers = get_user_followers(account['screen_name'])
    followers.append(tweet['user'])
    followers += retweeter_list
    nofollow_user_ids = get_not_follow_ids(followers)
    nofollow_user_ids = list(set(nofollow_user_ids))
    print(nofollow_user_ids)

    if nofollow_user_ids:
        for id in nofollow_user_ids:
            post_follow(id)

    print("SUCCESS!!")

    # except Exception as e:
    #     print("ERROR:", e)