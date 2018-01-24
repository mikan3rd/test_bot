import json


class TwitterApi:

    def __init__(self, twitter):
        self.api = twitter
        self.follow_count = 0
        self.unfollow_count = 0
        self.retweeter_count = 0

    def get_account(self):
        endpoint = 'https://api.twitter.com/1.1/account/settings.json'
        response = self.api.get(endpoint)
        return json.loads(response.text)

    def get_user_timeline(self, screen_name, count=200):
        endpoint = "https://api.twitter.com/1.1/statuses/user_timeline.json"
        params = {
            'screen_name': screen_name,
            'count': count,
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
        status,
        media_ids=None,
        in_reply_to_status_id=None,
    ):
        endpoint = "https://api.twitter.com/1.1/statuses/update.json"
        params = {'status': status}

        if in_reply_to_status_id:
            params['in_reply_to_status_id'] = in_reply_to_status_id

        if media_ids:
            params['media_ids'] = media_ids

        response = self.api.post(endpoint, params=params)
        return json.loads(response.text)

    def post_follow(self, user_id):
        if self.follow_count > 15:
            return {'errors': [{'code': '500'}]}

        endpoint = "https://api.twitter.com/1.1/friendships/create.json"
        params = {'user_id': user_id}
        response = self.api.post(endpoint, params=params)
        self.confirm_error(response)
        self.follow_count += 1
        return json.loads(response.text)

    def post_unfollow(self, user_id):
        if self.unfollow_count > 10:
            return {'errors': [{'code': '500'}]}

        endpoint = 'https://api.twitter.com/1.1/friendships/destroy.json'
        params = {'user_id': user_id}
        response = self.api.post(endpoint, params=params)
        self.confirm_error(response)
        self.unfollow_count += 1
        return json.loads(response.text)

    def get_user_followings(self, screen_name):
        endpoint = 'https://api.twitter.com/1.1/friends/list.json'
        params = {
            'screen_name': screen_name,
            'count': 200,
            'skip_status': True,
            'include_user_entities': False,
        }
        response = self.api.get(endpoint, params=params)
        self.confirm_error(response)
        return json.loads(response.text).get('users')

    def get_user_followers(self, screen_name):
        endpoint = "https://api.twitter.com/1.1/followers/list.json"
        params = {
            'screen_name': screen_name,
            'count': 200,
        }
        response = self.api.get(endpoint, params=params)
        self.confirm_error(response)
        return json.loads(response.text).get('users')

    def get_retweeters(self, id):
        if self.retweeter_count > 15:
            return {'errors': [{'code': '500'}]}

        endpoint = "https://api.twitter.com/1.1/statuses/retweets/" + \
            str(id) + ".json"
        params = {
            'trim_user': False,
        }
        response = self.api.get(endpoint, params=params)
        self.confirm_error(response)
        self.retweeter_count += 1
        return json.loads(response.text)

    def get_friendships_to_me(self, ids):
        endpoint = 'https://api.twitter.com/1.1/friendships/lookup.json'
        params = {
            'user_id': ids,
        }
        response = self.api.get(endpoint, params=params)
        self.confirm_error(response)
        return json.loads(response.text)

    def get_user_profile(self, user_id=None, screen_name=None):
        endpoint = 'https://api.twitter.com/1.1/users/show.json'
        params = {}
        if user_id:
            params['user_id'] = user_id
        elif screen_name:
            params['screen_name'] = screen_name
        response = self.api.get(endpoint, params=params)
        self.confirm_error(response)
        return json.loads(response.text)

    def confirm_error(self, raw_response):
        response = json.loads(raw_response.text)
        if isinstance(response, dict) and response.get("errors"):
            print(response.get("errors"))
            return False
        else:
            print("request OK")
            return True
