# coding: utf-8

from requests_oauthlib import OAuth1Session

import settings
from tweet import tweet_and_follow, unfollow
from api_twitter import TwitterApi

if __name__ == "__main__":

    print("start: kizuna_ai.py")

    twitter = OAuth1Session(
        settings.CONSUMER_KEY,
        settings.CONSUMER_SECRET,
        settings.ACCESS_TOKEN,
        settings.ACCESS_TOKEN_SECRET,
    )

    twitter_api = TwitterApi(twitter)

    query = '(キズナアイ OR #KizunaAI)' + \
        ' (filter:images OR filter:videos)' + \
        ' min_retweets:100'
    print("query:", query)

    unfollow(twitter_api)
    tweet_and_follow(twitter_api, query)
