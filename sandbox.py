import requests

token = 'AQAAAAA1ZV4rAAT7ozFhxJ47VUYgkXM9IImE1zk'
url = 'https://dialogs.yandex.net/api/v1/status'

headers = {'Host': 'https://dialogs.yandex.net/api/v1/status', f'Authorization': f'OAuth {token}'}

response = requests.get(url, headers=headers)

print(response.text)
