# -*- coding: utf-8 -*-
import random
import requests
from django.core.urlresolvers import reverse

session_request = requests.session()


def get_CSRF_val(urlPara):
    response = session_request.get(urlPara)
    try:
        return response.cookies["csrftoken"]
    except:
        raise ValueError

def get_one_doc_reader_block():
    dict_para = {
        "usage_id": "docreaderxblock.docreaderxblock.d0.u0",
        "handler_slug": "upload_proxy",
        "suffix": "student=student_1",
    }
    url = reverse("handler", kwargs=dict_para)
    return url


# def request_send_file_local(dict_obj):
#     # first we try to get the crsf token value.
#     dict_obj = {
#         "csrf_url": "http://127.0.0.1:9000/scenario/docreaderxblock.0/studio_view/",
#         "post_url": "http://127.0.0.1:9000/handler/docreaderxblock.docreaderxblock.d0.u0/upload_proxy/",
#         "host": "127.0.0.1:9000",
#         "file_name": "10.pdf",
#     }
#
#     host = dict_obj.get("host")
#     post_url = dict_obj.get("post_url")
#     csrf_url = dict_obj.get("csrf_url")
#     file_name = dict_obj["file_name"]
#
#     # if a csrfUrl is given, then we need to try to get the csrf token.
#     if csrf_url is not None:
#         try:
#             csrf_token = get_CSRF_val(csrf_url)
#         except:
#             csrf_token = None
#
#     # then we set up all the variables.
#     data = {
#         "allow_download": True,
#         "user_defined_name": str(random.random() * 100000),
#     }
#     requestDict = {
#         "http_method": "POST",
#         "headers":
#             {
#                 "X-CSRFToken": csrf_token,
#                 "host": host,
#             },
#         "params": {
#             "student": "student_1",
#         },
#     }
#     headers = requestDict["headers"]
#
#     url = post_url
#
#     files = {'file-upload': open(file_name, 'rb')}
#
#     response = session_request.post(post_url, params=requestDict["params"], data=data, files=files, headers=headers)
#
#     return response.text


# def requestSendFileServer(dict_obj):
#     raise NotImplementedError
#     # first we try to get the crsf token value.
#     resp = sessionRequest.get("http://127.0.0.1:9000/scenario/docreaderxblock.0/studio_view/")
#
#     # then we set up all the variables.
#     host = "127.0.0.1:9000"
#     file_name = dict_obj["file_name"]
#     data = {
#
#         "allow_download": True,
#         "user_defined_name": str(random.random() * 100000),
#     }
#
#     requestDict = {
#         "http_method": "POST",
#         "path": "/handler/docreaderxblock.docreaderxblock.d0.u0/upload_proxy",
#         "headers":
#             {
#                 "X-CSRFToken": resp.cookies["csrftoken"],
#                 "host": host,
#             },
#         "params": {
#             "student": "student_1",
#         },
#     }
#
#     headers = requestDict["headers"]
#
#     url = "http://" + host + "/handler/docreaderxblock.docreaderxblock.d0.u0/upload_proxy/"
#
#     files = {'file-upload': open(file_name, 'rb')}
#
#     response = sessionRequest.post(url, params=requestDict["params"], data=data, files=files, headers=headers)
#
#     return response.text
