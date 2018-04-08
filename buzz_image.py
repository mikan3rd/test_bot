# coding: utf-8

from requests_oauthlib import OAuth1Session

import settings
from tweet import tweet_and_follow, unfollow
from api_twitter import TwitterApi

if __name__ == "__main__":

    print("start: buzz_image.py")

    twitter = OAuth1Session(
        settings.BUZZ_IMAGE_CONSUMER_KEY,
        settings.BUZZ_IMAGE_CONSUMER_SECRET,
        settings.BUZZ_IMAGE_ACCESS_TOKEN,
        settings.BUZZ_IMAGE_ACCESS_TOKEN_SECRET,
    )

    twitter_api = TwitterApi(twitter)

    query = '(filter:images OR filter:videos) min_retweets:10000 lang:ja'
    print("query:", query)

    tweet_and_follow(twitter_api, query)
    unfollow(twitter_api)
