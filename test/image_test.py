import json
import os
import openai
import requests

#openai.api_key = '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'
# response = openai.Image.create(
#   prompt="a white siamese cat",
#   n=1,
#   size="1024x1024"
# )
# image_url = response['data'][0]['url']

values = (1, "John")
openai_api_key='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'
headers = {}
headers["Content-Type"] = "application/json"
headers["Authorization"] = "Bearer " + openai_api_key
data = {}
data["prompt"] = "一只猫与一只狗"
data["n"] = 1
data["size"] = "1024x1024"
url = 'https://api.openai.com/v1/images/generations'
#url = 'https://api.openai.com/v1/files' #检索所有图片文件
proxies_dev = {  # 针对urllib3最新版bug的手动设置代理
  'http': 'http://127.0.0.1:2080',
  'https': 'http://127.0.0.1:2080'
}
response = requests.post(url, data=json.dumps(data), headers=headers, proxies=proxies_dev)
#response = requests.get(url, headers=headers, proxies=proxies_dev)
print(response['text']['data'][0]['url'])

