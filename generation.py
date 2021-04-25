import json

import requests

fr_nw = requests.post("https://pelevin.gpt.dobro.ai/generate/",
                      data=json.dumps({"prompt": 'Он шел по лесу.', "length": 30})).json()
fr_nw = fr_nw['replies'][0]
print(fr_nw)
