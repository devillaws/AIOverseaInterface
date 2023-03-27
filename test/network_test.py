import os
import tiktoken
from ping3 import ping
print(os.environ.get('http_proxy'))
print(os.environ.get('https_proxy'))
import requests

proxies_http = {
                'http': 'http://127.0.0.1:2080',
                'https': 'http://127.0.0.1:2080'
            }
proxies_socks = {
                'http': 'socks5h://127.0.0.1:2080',
                'https': 'socks5h://127.0.0.1:2080'
            }
#url = "https://www.google.com/"
url = 'https://api.openai.com/v1/chat/completions'

def request_test(url):
    try:
        #response = requests.get(url, proxies=proxies_http)
        response = requests.post(url, proxies=proxies_http)
        if response.status_code == 200:
            print("网站可以访问！success")
        else:
            print("网站无法访问！fail")
    except Exception as e:
        print("网站无法访问，错误信息：", e)



def ping_test(host, timeout=5):
    try:
        response_time = ping(host, timeout=timeout)
        if response_time is not None:
            print(f"{host} is reachable. Response time: {response_time} ms")
        else:
            print(f"{host} is not reachable.")
    except Exception as e:
        print(f"Error pinging {host}: {e}")


#ping_test(url)
#request_test(url)
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0301")