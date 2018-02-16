# coding: utf-8

import random
import re
import requests

from pprint import pprint


# スクレイピング
def get_user_ids_of_post_likes(post_id):
    url = 'https://twitter.com/i/activity/favorited_popup?id=' + str(post_id)
    json_data = requests.get(url).text
    found_ids = re.findall(r'data-user-id=\\"+\d+', json_data)
    unique_ids = list(
        set([re.findall(r'\d+', match)[0]for match in found_ids]))
    print("scraping SUCCESS")
    return unique_ids


# その他
def get_media_ids(tweets):
    media_ids = []

    for tweet in tweets:

        if tweet.get('quoted_status'):
            tweet = tweet['quoted_status']

        media_list = get_media_from_tweet(tweet)

        if media_list is None:
            print("mine: NOT FOUND")
            continue

        for media in media_list:
            if media.get('type') == 'video':
                media_ids.append(get_video_info(media.get("video_info")))
            else:
                media_ids.append(media.get("url"))

    return media_ids


def get_tweet_index(tweets, media_ids, twitter_api):
    tweet_index = random.randint(0, len(tweets))

    for index, tweet in enumerate(tweets):

        media_list = get_media_from_tweet(tweet)

        if media_list is None:
            print("search: NOT FOUND")
            continue

        for media in media_list:
            url = media.get("url")
            if media.get('type') == 'video':
                url = get_video_info(media.get("video_info"))

            if url in media_ids:
                break

        else:
            response = twitter_api.post_follow(tweet['user']['id'])
            if response.get('errors'):
                continue

            tweet_index = index
            break

    return tweet_index


def create_tweet_content(tweet):
    url_list = re.findall('https://t.co/\S*', tweet['text'])
    tweet['text'] = tweet['text'][:-(len(url_list[-1]))]

    over_len = len(tweet['text']) - 80

    if over_len > 0:
        print("Too long!!")
        tweet['text'] = tweet['text'][:-over_len]
        tweet['text'] += "... "
        tweet['text'] = re.sub('(http|#|@)\S*\.\.\.', '...', tweet['text'])

    media_list = get_media_from_tweet(tweet)

    url_list = []
    for media in media_list:
        if media.get('type') == 'video':
            url_list.append(get_video_info(media.get("video_info")))
        else:
            url_list.append(media.get("url"))

    urls = ' '.join(url_list)

    screen_name = tweet['user']['screen_name']
    tweet_list = []
    tweet_list.append(tweet['text'] + '\n')
    tweet_list.append("ツイート元: @" + screen_name)
    tweet_list.append(
        'https://twitter.com/' + screen_name +
        '/statuses/' + str(tweet['id'])
    )
    tweet_list.append(urls)
    tweet_content = '\n'.join(tweet_list)
    return tweet_content


def get_media_from_tweet(tweet):
    extended_entities = tweet.get('extended_entities')
    if extended_entities:
        return extended_entities.get('media')

    urls = tweet.get('entities').get('urls')
    if urls:
        return urls

    return None


def get_video_info(video_info):
    variants = video_info.get('variants')
    video_list = []
    for variant in variants:
        if variant.get('bitrate'):
            video_list.append(variant)

    video_list = sorted(video_list, key=lambda k: k['bitrate'], reverse=True)
    return video_list[0]['url']


def get_not_follow_ids_by_user(users):
    ids = []
    for user in users:
        following = user.get('following')
        follow_request_sent = user.get('follow_request_sent')
        if following is False and follow_request_sent is False:
            ids.append(user['id'])
    return ids


def get_not_follow_ids(followers, ids):
    follow_ids = {follower['id'] for follower in followers}
    return list(set(ids) - follow_ids)


def tweet_and_follow(twitter_api, query):
    # try:
    account = twitter_api.get_account()

    timeline_tweets = twitter_api.get_user_timeline(
        account['screen_name'])
    media_ids = get_media_ids(timeline_tweets)

    tweets = twitter_api.search_tweet(query)
    tweets = sorted(tweets, key=lambda k: k['retweet_count'], reverse=True)
    index = get_tweet_index(tweets, media_ids, twitter_api)
    tweet = tweets[index]
    tweet_content = create_tweet_content(tweet)
    print(tweet_content)

    response = twitter_api.post_tweet(
        status=tweet_content,
        in_reply_to_status_id=tweet['id'],
    )

    if response.get("errors") is None:
        print("Tweet SUCCESS!!")

    else:
        print(response.get("errors"))

    tweet_ids = []
    for timeline_tweet in timeline_tweets:
        if timeline_tweet['retweet_count'] > 0:
            tweet_ids.append(timeline_tweet['id'])

    retweeter_list = []
    like_user_ids = []

    for tweet_id in tweet_ids:
        retweet_list = twitter_api.get_retweeters(tweet_id)
        like_user_ids += get_user_ids_of_post_likes(tweet_id)

        if isinstance(retweet_list, dict) and retweet_list.get("errors"):
            break

        for retweet in retweet_list:
            retweeter_list.append(retweet['user'])

    followers = twitter_api.get_user_followers(account['screen_name'])
    followings = twitter_api.get_user_followings(account['screen_name'])

    users = []
    users += followers
    users += retweeter_list
    nofollow_user_ids = get_not_follow_ids_by_user(users)
    nofollow_user_ids += get_not_follow_ids(followings, like_user_ids)
    nofollow_user_ids = list(set(nofollow_user_ids))
    print(nofollow_user_ids)

    if nofollow_user_ids:
        for id in nofollow_user_ids:
            response = twitter_api.post_follow(id)
            errors = response.get("errors")
            if errors:
                code = [error.get('code') for error in errors]
                if 161 in code or 500 in code:
                    break

    print("Follow SUCCESS!!")

    # except Exception as e:
    #     print("ERROR:", e)


def unfollow(twitter_api):
    account = twitter_api.get_account()
    profile = twitter_api.get_user_profile(screen_name=account['screen_name'])

    if profile.get('followers_count') > profile.get('friends_count') - 50:
        print("Don't have to Unfollow!!")
        return

    followings = twitter_api.get_user_followings(account['screen_name'])
    print("followings:", len(followings))
    following_id_list = [
        str(following.get('id'))
        for following in followings[100:]
    ]
    following_ids = ','.join(following_id_list)
    user_list = twitter_api.get_friendships_to_me(following_ids)
    not_followed_id_list = [
        user.get('id') for user in user_list
        if "followed_by" not in user.get('connections')
    ]
    for id in not_followed_id_list:
        response = twitter_api.post_unfollow(id)
        if response.get('screen_name'):
            print(response.get('screen_name'))
        else:
            break

    print("Unfollow SUCCESS!!")
