# -*- coding: utf-8 -*-
# # @Time    : 2019-08-01 11:12
# # @Author  : Joe
# # @Site    :
# # @File    : gitlabapi.py
# # @Software: PyCharm
# # @function: xxxxx


import json
import uuid
from urllib import request

# gitlab地址
gitlab_url = 'xxxx'
# gitlab token
gitlab_token = 'xxxx'
headers = {'PRIVATE-TOKEN': gitlab_token}

req = request.Request(gitlab_url, headers=headers)
response = request.urlopen(req)
output = response.read().decode('utf-8')
output = json.loads(output)
print(output)

# for i in output:
#     print(i['name'])

# if __name__ == '__main__':
    # gitlab_projects()
    # gitlab_groups()
    # gitlab_namsspace()