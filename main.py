from aip import AipFace  # AI core
import base64  # for encode use

'''APP Detail'''
APP_ID = '17074468'
API_ID = 'tBs6GAGhr1hRow3KacUtQGGk'
SECRET_KEY = 'A4iSePxNobpGFSupM4XTV0McSoqKqyFt'

client = AipFace(APP_ID, API_ID, SECRET_KEY)  # Online detect client

with open("//Users//bruce//Pictures//IMG_1334.jpeg", "rb") as f:
    base64_data = base64.b64encode(f.read())
    # print(base64_data)  # encode check

image = str(base64_data, 'utf-8')
# error record: error_code:222203 image check fail
# solution: specific type convert: utf-8
imageType = "BASE64"
groupIdList = "test"

result = client.search(image, imageType, groupIdList);

print(result)

