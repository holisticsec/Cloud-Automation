#get list of public ip and elastic ip in all accounts using Prisma Cloud API

import json
import ipaddress
import sys
import requests

ACCESS_KEY = sys.argv[1]
SECRET_KEY = sys.argv[2]
CLOUD_TYPE = 'aws'
URL = 'https://<tenant>.prismacloud.io/search/config'


def api_login(ACCESS_KEY, SECRET_KEY):
    headers = {'accept': 'application/json; charset=UTF-8', 'Content-Type': 'application/json'}
    api_url = 'https://<tenant>.prismacloud.io/login'
    action = 'POST'
    data = {}
    data['username'] = ACCESS_KEY
    data['password'] = SECRET_KEY
    data_json = json.dumps(data)
    response_raw = requests.request(action, api_url, headers=headers, data=data_json)
    response_data = response_raw.json()
    token = response_data['token']
    return token

#get both public and elastic ip
def get_public_elastic_ip():
    all_ip = list()
    publicip_list = list()
    elasticip_list = list()
    token = api_login(ACCESS_KEY, SECRET_KEY)
    headers = {"Accept": "application/json; charset=UTF-8", "Content-Type": "application/json; charset=UTF-8",
               "x-redlock-auth": token}
    #get public ip list           
    payload = json.dumps({
        "query": "config from cloud.resource where api.name = 'aws-ec2-describe-instances' and json.rule = publicIpAddress exists",
        "timeRange": {
            "type": "relative",
            "value": {
                "unit": "hour",
                "amount": 24
            }
        }
    })
    response = requests.request("POST", URL, data=payload, headers=headers)
    data = response.json()
    for i in data["data"]["items"]:
        publicip_list.append(i["data"]["publicIpAddress"])

    #get elastic ip list
    payload = json.dumps({
        "query": "config from cloud.resource where api.name = 'aws-ec2-elastic-address' AND json.rule = publicIp exists ",
        "timeRange": {
            "type": "relative",
            "value": {
                "unit": "hour",
                "amount": 24
            }
        }
    })
    response = requests.request("POST", URL, data=payload, headers=headers)
    data = response.json()
    for i in data["data"]["items"]:
        elasticip_list.append(i["data"]["publicIp"])
    all_ip = publicip_list + elasticip_list
    return set(all_ip)


if __name__ == '__main__':
    all_ip_set = get_public_elastic_ip()
    print(*all_ip_set, sep='\n')
    