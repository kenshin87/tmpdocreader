from baidubce.auth.bce_credentials import BceCredentials
from django.conf import settings
import os

"""
    Baidu AK and SK should be placed inside settings.py. If they are absent, then use the value inside "except" which is read from "keys.json"
"""

try:
    access_key_id = settings.BAIDU_AK
    secret_access_key = settings.BAIDU_SK
except:
    import json

    path = os.path.join(os.getcwd(), "docreaderxblock/docreaderxblock/doc/keys.json")
    if not os.path.isfile(path):
        path = os.path.join(os.path.dirname(os.getcwd()), "docreaderxblock/docreaderxblock/doc/keys.json")
    assert os.path.isfile(path)
    baidu_key_string = open(path, "r").read()

    baidu_dict = json.loads(baidu_key_string)

    access_key_id = str(baidu_dict["access_key_id"])
    secret_access_key = str(baidu_dict["secret_access_key"])

credentials = BceCredentials(access_key_id, secret_access_key)