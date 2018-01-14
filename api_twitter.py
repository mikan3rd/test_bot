import json


class TwitterApi:

    def __init__(self, twitter):
        self.api = twitter

    def get_account(self):
        endpoint = 'https://api.twitter.com/1.1/account/settings.json'
        response = self.api.get(endpoint)
        return json.loads(response.text)

    def get_user_timeline(self, screen_name):
        endpoint = "https://api.twitter.com/1.1/statuses/user_timeline.json"
        params = {
            'screen_name': screen_name,
            'count': 200,
        }
        response = self.api.get(endpoint, params=params)
        return json.loads(response.text)

    def search_tweet(self, query):
        endpoint = "https://api.twitter.com/1.1/search/tweets.json"
        params = {
            'q': query,
            'count': 100,
        }
        response = self.api.get(endpoint, params=params)
        return json.loads(response.text).get('statuses')

    def post_tweet(
        self,
        tweet,
        in_reply_to_status_id=None,
    ):
        endpoint = "https://api.twitter.com/1.1/statuses/update.json"
        params = {'status': tweet}

        if in_reply_to_status_id:
            params['in_reply_to_status_id'] = in_reply_to_status_id

        response = self.api.post(endpoint, params=params)
        return json.loads(response.text)

    def post_follow(self, user_id):
        endpoint = "https://api.twitter.com/1.1/friendships/create.json"
        params = {'user_id': user_id}
        response = self.api.post(endpoint, params=params)
        return json.loads(response.text)

    def get_user_followers(self, screen_name):
        endpoint = "https://api.twitter.com/1.1/followers/list.json"
        params = {
            'screen_name': screen_name,
            'count': 200,
        }
        response = self.api.get(endpoint, params=params)
        return json.loads(response.text).get('users')

    def get_retweeters(self, id):
        endpoint = "https://api.twitter.com/1.1/statuses/retweets/" + \
            str(id) + ".json"
        params = {
            'trim_user': False,
        }
        response = self.api.get(endpoint, params=params)
        return json.loads(response.text)
