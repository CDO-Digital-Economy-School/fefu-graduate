import re
import numpy as np
import pandas as pd
import requests
from json import JSONDecoder


vk_api = 'https://api.vk.com/method/'
decoder = JSONDecoder()


class Params:

    def __init__(self, api_version, access_token, **kwargs):
        self.params_dict = {
            'v': api_version,
            'filter': 'all',
            'lang': 'ru',
            'access_token': access_token
            # keyring.get_password('vk_api', input('insert username'))
        }
        for key, value in kwargs.items():
            self.add(key, value)

    def add(self, key, value):
        self.params_dict[key] = str(value)

    def remove(self, key):
        self.params_dict.pop(key)

    def get_dict(self):
        return self.params_dict


def get_request_result(method, params, inner_obj=''):
    result = requests.get(vk_api + method, params=params)

    try:
        if inner_obj == '':
            return decoder.decode(result.text)['response']
        else:
            return decoder.decode(result.text)['response'][inner_obj]
    except:
        error = decoder.decode(result.text)
        print(error['error']['error_msg'])
        if inner_obj == 'count':
            return 0
        else:
            return []


class Group:
    def __init__(self, group_id):
        self.group_id = group_id
        self.method = 'groups.getMembers'
        self.params = Params(group_id=group_id, method=self.method)

    def get_members_count(self):
        users_count = get_request_result(self.method, self.params.get_dict(), 'count')
        return users_count

    def get_members_batch(self, count=100, offset=0):
        self.params.add('count', count)
        self.params.add('offset', offset)

        members_batch = get_request_result(self.method, self.params.get_dict(), 'users')

        self.params.remove('count')
        self.params.remove('offset')
        return members_batch

    def get_members_all(self):
        self.members = []

        for i in range((self.get_members_count() // 100) + 1):
            self.members = self.members + self.get_members_batch(count=100, offset=i * 100)
        return self.members


class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.params = Params(user_id=user_id)

    def get_user_info(self):
        self.user_info = get_request_result('users.get', self.params.get_dict())
        return self.user_info

    def get_friends_count(self):
        friends_count = get_request_result('friends.get', self.params.get_dict(), 'count')
        return friends_count

    def get_friends_batch(self, count, offset=0, fields='nickname'):
        self.params.add('count', count)
        self.params.add('offset', offset)
        self.params.add('fields', fields)
        friends_batch = get_request_result('friends.get', self.params.get_dict(), 'items')
        self.params.remove('count')
        self.params.remove('offset')
        self.params.remove('fields')
        return friends_batch

    def get_friends_all(self):
        self.friends = []
        for i in range((self.get_friends_count() // 100) + 1):
            self.friends = self.friends + self.get_friends_batch(count=100, offset=i * 100, fields='nickname')
        return self.friends

    def get_groups_count(self):
        groups_count = get_request_result('groups.get', self.params.get_dict(), 'count')
        return groups_count

    def get_groups_batch(self, count, offset=0):
        self.params.add('count', count)
        self.params.add('offset', offset)
        groups_batch = get_request_result('groups.get', self.params.get_dict(), 'items')
        self.params.remove('count')
        self.params.remove('offset')
        return groups_batch

    def get_groups_all(self):
        self.groups = []
        for i in range((self.get_groups_count() // 100) + 1):
            self.groups = self.groups + self.get_groups_batch(count=100, offset=i * 100)
        return self.groups


class Users:
    def __init__(self, user_ids):
        self.user_ids = user_ids
        self.params = Params(user_ids=user_ids)

    def get_users_info(self):
        self.users_info = get_request_result('users.get', self.params.get_dict())
        return self.users_info