import time
from .auth_keys import credentials
from .authorization_generator import sign
from .authorization_generator import get_baidu_time_stamp
from docreaderxblock.reader_settings import BUCKET_NAME
import requests
import json

class DocWrapper(object):

    @staticmethod
    def status_by_doc_id(dict_obj):
        """
            depends on info_by_doc_id
        """
        responsed_text = DocWrapper.info_by_doc_id(dict_obj)
        responsed_text_dict = json.loads(responsed_text)
        try:
            status = responsed_text_dict["status"]
            return status
        except:
            return None

    @staticmethod
    def info_by_doc_id(dict_obj):
        """
            GET /v<version>/document/<documentId> HTTP/1.1
            host: doc.bj.baidubce.com
            content-type: application/json
            authorization: <bce-authorization-string>
        """

        document_id_string_para = dict_obj["baidu_doc_id"]

        host = "doc.bj.baidubce.com"

        requestDict = {
            "credentials": credentials,
            "http_method": "GET",
            "path": "/v2/document/" + document_id_string_para,

            "headers":
                {
                    "content-type": "application/json",
                    "host": host,
                    "Date": get_baidu_time_stamp(),
                },
            "timestamp": int(time.time()),
            "params": None,
        }

        result = sign(**requestDict)

        headers = requestDict["headers"]

        headers.update(
            {"authorization": result}
        )

        url = "https://" + host + "/v2/document/" + document_id_string_para

        gmtTime = get_baidu_time_stamp()
        response = requests.get(url, headers=headers)

        return response.text

    @staticmethod
    def build_doc_from_bos(dict_obj):
        """
            POST /v<version>/document?source=bos HTTP/1.1
            host: doc.bj.baidubce.com
            authorization: <bce-authorization-string>
            content-type: application/json
        """

        host = "doc.bj.baidubce.com"

        file_name = dict_obj["file_name"]
        if dict_obj.get("bucket_name") is not None:
            bucket_name = dict_obj.get("bucket_name")
        else:
            bucket_name = BUCKET_NAME

        file_name_title = file_name.split(".")[0]
        file_name_format = file_name.split(".")[1]

        data = {
            "bucket": bucket_name,
            "object": file_name,
            "title": file_name_title,
            "format": file_name_format,
        }

        data = json.dumps(data, separators=(',', ':'))

        length = len(data)

        requestDict = {
            "credentials": credentials,
            "http_method": "POST",
            "path": "/v2/document",
            "headers":
                {
                    "Content-Length": str(length),
                    "content-type": "application/json",
                    "host": host,
                    "Date": get_baidu_time_stamp(),
                },
            "timestamp": int(time.time()),
            "params": {
                "source": "bos",
            },
        }

        result = sign(**requestDict)

        headers = requestDict["headers"]

        headers.update(
            {"authorization": result}
        )

        url = "https://" + host + "/v2/document"

        gmtTime = get_baidu_time_stamp()
        response = requests.post(url, params=requestDict["params"], data=data, headers=headers)

        return response.text

    @staticmethod
    def check_published(dict_obj):
        baidu_doc_id = dict_obj["baidu_doc_id"]
        returned_string = DocWrapper.get_public_status(baidu_doc_id)
        returned_dict = json.loads(returned_string)
        return returned_dict["status"]

    @staticmethod
    def get_public_status(document_id):
        """
            GET /v<version>/document/<documentId> HTTP/1.1
            host: doc.bj.baidubce.com
            content-type: application/json
            authorization: <bce-authorization-string>
        """
        host = "doc.bj.baidubce.com"

        requestDict = {
            "credentials": credentials,
            "http_method": "GET",
            "path": "/v2/document/" + document_id,
            "headers":
                {
                    "content-type": "application/json",
                    "host": host,
                    "Date": get_baidu_time_stamp(),
                },
            "timestamp": int(time.time()),
            "params": None,
        }

        result = sign(**requestDict)

        headers = requestDict["headers"]

        headers.update(
            {"authorization": result}
        )

        url = "https://" + host + requestDict["path"]
        # url = "http://127.0.0.1:80/v2/document"


        gmtTime = get_baidu_time_stamp()
        response = requests.get(url, headers=headers)

        return response.text

