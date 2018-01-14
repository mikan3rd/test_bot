# coding: utf-8

from requests_oauthlib import OAuth1Session

import settings
from tweet import tweet_and_follow

if __name__ == "__main__":

    print("start: splatoon.py")

    twitter = OAuth1Session(
        settings.CONSUMER_KEY_SPLATOON,
        settings.CONSUMER_SECRET_SPLATOON,
        settings.ACCESS_TOKEN_SPLATOON,
        settings.ACCESS_TOKEN_SECRET_SPLATOON,
    )
    query = '#Splatoon2 filter:videos min_retweets:50'
    print("query:", query)

    tweet_and_follow(twitter, query)
