import requests
from urllib.parse import urljoin
from yandex_tracker_client import TrackerClient

org_id = "7718060"
oath_auth="y0_AgAAAAAaUsuYAAmqyAAAAADgie4N5wEwUUfgS-2Er7LePE_mtI-4i8o"

base_url = "https://api.tracker.yandex.net"

headers = {}
#headers["Host"] = base_url
headers["X-Org-ID"]=org_id
headers['Content-Type'] = 'application/json'
headers['Authorization'] = 'OAuth ' + oath_auth
path = "/v2/queues/"
#headers['If-Match'] = '"{}"'.format('v2')

url = urljoin(base_url,path)
response = requests.get(url, headers=headers)
print(response.json())
#tracker_client = TrackerClient(oath_auth, org_id)

pass
pass