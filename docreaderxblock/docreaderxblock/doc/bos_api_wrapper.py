# -*- coding: UTF-8 -*-

import time
import json
import time
import requests
from baidubce import exception
from baidubce.services import bos
from baidubce.services.bos import canned_acl
from baidubce.services.bos.bos_client import BosClient
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials

import requests

from .auth_keys import credentials
from .authorization_generator import get_baidu_time_stamp
from .authorization_generator import sign

from docreaderxblock import reader_settings

bos_host = "bj.bcebos.com"

config = BceClientConfiguration(
   credentials=credentials,
   endpoint = bos_host
)



#新建BosClient
bos_client = BosClient(config)

try:
    bocket_name = reader_settings.BUCKET_NAME
except:
    bucket_name = "adorable"


"""Followings are api that are already wrapped inside baidubce"""
def upload_file_to_bos(dict_obj):

    file_name = dict_obj["file_name"]
    abs_path = dict_obj["abs_path"]

    if type(file_name) == unicode:
        file_name = str(file_name)

    if type(abs_path) == unicode:
        abs_path = str(abs_path)

    try:
        returned_str = bos_client.put_object_from_file(bucket_name, file_name, abs_path)
        return True
    except Exception as e:
        print e
        return False

def check_file_from_bos(dict_obj):

    file_name = dict_obj["file_name"]
    if dict_obj.get("bucket_name") is not None:
        bucket_name = dict_obj.get("bucket_name")
    else:
        bucket_name = reader_settings.BUCKET_NAME

    if type(file_name) != str:
        file_name = str(file_name)
    if type(bucket_name) != str:
        bucket_name = str(bucket_name)

    try:
        returned_info = bos_client.get_object_meta_data(bucket_name, file_name)
        return True
    except:
        return False



"""Followings are apis that define by the web interface, so here we use requests.methods"""


def get_bos_blob(dict_para):
    """
    GET /<ObjectKey> HTTP/1.1
    Host: <BucketName>.bj.bcebos.com
    Date: <Date>
    Authorization: <Authorization_String>
    Range: <Range_String>
        We only support 1 bucket's sts. So the resource parameter here is just a bucket name instead
    of a list of name
    """
    try:
        bucket_name = dict_para["bucket_name"]
    except:
        bucket_name = bucket_name

    file_name = dict_para["file_name"]

    print bucket_name
    print file_name

    #bucket_name = "testing-yingli"
    #file_name = "1516156204551150048.pdf"

    host = bucket_name + ".bj.bcebos.com"

    requestDict = {
        "credentials": credentials,
        "http_method": "GET",
        "path": "/1516156204551150048.pdf",
        "headers":
            {

                "host": host,
                "Date": get_baidu_time_stamp(),
            },
        "timestamp": int(time.time()),
        "params": None,
    }

    result = sign(**requestDict)

    url = "https://" + host + "/1516156204551150048.pdf"

    headers = {
        'date': get_baidu_time_stamp(),
        'authorization': result,
        'host': host,
    }

    response = requests.request("GET", url, headers=headers)

    return response.text


def get_sts_dict(dict_para):
    return get_sts_parser(get_sts(dict_para))

def get_sts_parser(json_string):
    return json.loads(json_string)

def get_sts(dict_para):
    """
        POST /v1/sessionToken HTTP/1.1
        Host: sts.bj.baidubce.com
        Date: Wed, 06 Apr 2016 06:34:40 GMT
        Authorization: AuthorizationString
        Content-type:application/json
        Content-Length:178

        We only support 1 bucket's sts. So the resource parameter here is just a bucket name instead
    of a list of name
    """
    try:
        bucket_name = dict_para["bucket_name"]
        resource = bucket_name + "/*"
    except:
        raise ValueError
    try:
        permission  = dict_para["permission"]
    except:
        permission = ["READ", "LIST", "WRITE"]

    data = {
        "accessControlList":
            [
                {
                    "service": "bce:bos",
                    "region": "bj",
                    "effect": "Allow",
                    "resource": [resource],
                    "permission": permission,
                }
            ]
    }

    data = json.dumps(data, separators=(',', ':'))
    length = str(len(data))

    requestDict = {
        "credentials": credentials,
        "http_method": "POST",
        "path": "/v1/sessionToken",
        "headers":
            {
                "host": "sts.bj.baidubce.com",
                "Date": get_baidu_time_stamp(),
                "content-length": length,
            },
        "timestamp": int(time.time()),
        "params": None,
    }

    result = sign(**requestDict)

    url = "http://sts.bj.baidubce.com/v1/sessionToken"

    headers = {
        'date': get_baidu_time_stamp(),
        'authorization': result,
        'host': "sts.bj.baidubce.com",
        "content-length": length,
    }

    gmtTime = get_baidu_time_stamp()
    response = requests.request("POST", url, data=data, headers=headers)

    return response.text





def get_document_link_string(document_id):
    return get_document_link_parser(get_document_link(document_id))

def get_document_link_parser(json_para):
    try:
        return json.loads(json_para)["downloadUrl"]
    except:
        return ""

def get_document_link(document_id):

    host = "doc.bj.baidubce.com"
    path = "/v2/document/" + document_id

    requestDict = {
         "credentials": credentials,
         "http_method":"GET",
         "path" : path,
         "headers":
             {
                 'Date': get_baidu_time_stamp(),
                 "host": host,
                 "Content-Type": "application/json",
             },
         "timestamp": int(time.time()),
         "params": {
         "documentId":document_id,
         "expireInSeconds": -1,
         "download": "",
         },
     }

    result = sign(**requestDict)

    url = "http://" + host + path

    headers = {
         'Date': get_baidu_time_stamp(),
         'authorization': result,
         "Content-Type": "application/json",
         "host": "doc.bj.baidubce.com",
    }

    gmtTime = get_baidu_time_stamp()
    response = requests.request("GET", url, params=requestDict["params"], headers=headers)

    return response.text

def get_buckets():

    requestDict = {
        "credentials": credentials,
        "http_method":"GET",
        "path" : "/",
        "headers":
            {
                "host": "bj.bcebos.com",
            },
        "timestamp": int(time.time()),
        "params": None,
    }

    result = sign(**requestDict)

    url = "https://bj.bcebos.com/"

    headers = {
        'date': get_baidu_time_stamp(),
        'authorization': result,
        'host': "bj.bcebos.com",
    }

    response = requests.request("GET", url, headers=headers)

    return response.text

def list_files_of_bucket(bucket_name_string_para):

    requestDict = {
        "credentials": credentials,
        "http_method":"GET",
        "path" : "/",
        "headers":
            {
                "host": bucket_name_string_para + "." + "bj.bcebos.com",
            },
        "timestamp": int(time.time()),
        "params": None,
    }

    result = sign(**requestDict)

    url = "https://bj.bcebos.com/"

    headers = {
        'date': get_baidu_time_stamp(),
        'authorization': result,
        'host': "bj.bcebos.com",
    }

    response = requests.request("GET", url, headers=headers)

    return response.text