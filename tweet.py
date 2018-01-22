# coding: utf-8

import random
import re
import requests


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

        if tweet.get('entities').get('media'):
            media_list = tweet['entities']['media']
        else:
            media_list = tweet['entities']['urls']

        for media in media_list:
            media_ids.append(media.get("url"))

    return media_ids


def get_tweet_index(tweets, media_ids):
    tweet_index = random.randint(0, len(tweets))

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

    timeline_tweets = twitter_api.get_user_timeline(account['screen_name'])
    media_ids = get_media_ids(timeline_tweets)

    tweets = twitter_api.search_tweet(query)
    tweets = sorted(tweets, key=lambda k: k['retweet_count'], reverse=True)
    index = get_tweet_index(tweets, media_ids)
    tweet = tweets[index]
    tweet_content = create_tweet_content(tweet)
    print(tweet_content)

    response = twitter_api.post_tweet(
        tweet_content,
        in_reply_to_status_id=tweet['id'],
    )

    if response.get("errors") is None:
        print("Tweet SUCCESS!!")

    tweet_ids = []
    for timeline_tweet in timeline_tweets:
        if timeline_tweet['retweet_count'] > 0:
            tweet_ids.append(timeline_tweet['id'])

    retweeter_list = []
    like_user_ids = []

    for tweet_id in tweet_ids:
        retweet_list = twitter_api.get_retweeters(tweet_id)
        like_user_ids += get_user_ids_of_post_likes(tweet_id)

        for retweet in retweet_list:
            retweeter_list.append(retweet['user'])

    followers = twitter_api.get_user_followers(account['screen_name'])

    users = []
    users += followers
    users.append(tweet['user'])
    users += retweeter_list
    nofollow_user_ids = get_not_follow_ids_by_user(users)
    nofollow_user_ids += get_not_follow_ids(followers, like_user_ids)
    nofollow_user_ids = list(set(nofollow_user_ids))
    print(nofollow_user_ids)

    if nofollow_user_ids:
        for id in nofollow_user_ids:
            twitter_api.post_follow(id)

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
