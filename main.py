import os
import json
import time

from vkauth import VKAuth
import vktool as vk

FEFU_ID = 415 # ID of FEFU in VK database
SLEEP_TIME = 3

app_id = ... #todo use ID of your application
api_v = '5.89'
permissions = ('notify,friends,photos,audio,video,stories,pages,status,notes,wall,ads,offline,docs,groups,notifications,stats,email,market').split(',')
auth = VKAuth(permissions, app_id, api_v)
auth.auth()
token = auth.get_token()
root = os.path.dirname(os.path.abspath(__file__))


def read_data_from_file(filename='data.csv'):
    raw_data = dict()

    with open(os.path.join(root, 'data', filename), 'r') as fdata:
        data = fdata.readlines()
        for data_item in data:
            user_name, grad_year = tuple(data_item.split(';'))
            grad_year = grad_year
            raw_data[user_name] = grad_year

    return raw_data


def get_name_parts(name):
    arr = name.split()
    second_name, second_name = arr[0], arr[1] # second name, name, father's
    return first_name, second_name


def parse_career_info(data):
    if data.get('career', None) is None:
        return {}

    res = {}
    for career in data['career']:
        if career.get('company', None):
            res['company'] = career.get('company', '')
        if career.get('group_id', None):
            res['group_id'] = career.get('group_id', '')
        if career.get('position', None):
            res['position'] = career.get('position', '')
        if career.get('from', None):
            res['from'] = career.get('from', '')
        if career.get('until', None):
            res['until'] = career.get('until', '')

    return res


qparams = vk.Params(
    api_version=api_v,
    access_token=token
)


data = read_data_from_file()
json_out_data = list()
fout = open(os.path.join(root, 'data', 'data_out.csv'), 'w')


idx = 0
user_ids = list()
for full_name, year in data.items():
    first_name, last_name = get_name_parts(full_name)
    idx += 1
    qparams.add('q', '{} {}'.format(first_name, last_name))
    #qparams.add('university', fefu_id)
    qparams.add('university_year', int(year))
    print('{} Try search user {} {}'.format(idx, first_name, last_name))
    response = vk.get_request_result(method='users.search', params=qparams.get_dict())
    print(response)
    for idx, item in enumerate(response['items']):
        #todo check profile is_closed or is_opened
        user_id = item['id']

        print("\r User id={} name={} {}\n".format(user_id, first_name, last_name))
        user_ids.append(user_id)
        print("Add user_id={}".format(user_id))
    qparams.remove('q')
    qparams.remove('university_year')
    #time.sleep(SLEEP_TIME)


qparams.add('user_ids', ','.join([ str(x) for x in user_ids]))
qparams.add('fields', 'career,education')


json_out_data = []
response = vk.get_request_result(method='users.get', params=qparams.get_dict())
print("Start process career for every user with id={}".format(','.join([ str(x) for x in user_ids])))
print(response)


for idx, user_item in enumerate(response):
    print(type(user_item))
    json_out_data.append({
        'id': user_item['id'],
        'full_name': '{} {}'.format(user_item['first_name'], user_item['last_name']),
        'university': 'ДВФУ',
        'graduation_year': user_item.get('graduation', ''),
        'career': parse_career_info(user_item)
    })


print('Start process json-output file\n')
with open(os.path.join(root, 'data', 'data_out.json'), 'w') as fout:
    json.dump(json_out_data,
              fout,
              indent=4,
              ensure_ascii=False)