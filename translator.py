import urllib.request
import json


str1 = "I like burger"

# Papago
def init_api():
    client_id = "[your id]"
    client_secret = "[your secret]"
    url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
    request = urllib.request.Request(url)
    request.add_header("X-NCP-APIGW-API-KEY-ID",client_id)
    request.add_header("X-NCP-APIGW-API-KEY",client_secret)
    return request

def translate_papago(request, _text):
    request = init_api()
    encText = urllib.parse.quote(_text)
    data = "source=en&target=ko&text=" + encText
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        rjson = json.loads(response_body.decode())
        return rjson['message']['result']['translatedText']
    else:
        print("Error Code:" + rescode)
        return -1
