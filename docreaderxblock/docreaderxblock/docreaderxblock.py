# -*- coding: utf-8 -*-
"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, Boolean
from xblock.fragment import Fragment

import os
import six
import urlparse
import json
import time
import random
from functools import partial

from webob.response import Response
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.template import Context, Template
from django.conf import settings
from django.core import exceptions
from django.http import Http404, HttpResponseBadRequest, HttpResponse, StreamingHttpResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.http import JsonResponse

from .file_helper import store_uploaded_file
from .reader_settings import MEDIA_ROOT
from .reader_settings import ALLOWED_UPLOAD_FILE_TYPE
from .reader_settings import MAX_UPLOAD_FILE_SIZE
from .reader_settings import get_address
from .reader_settings import doc_fs
from .reader_settings import reverse_wrapper


from .doc.bos_api_wrapper import upload_file_to_bos
from .doc.bos_api_wrapper import check_file_from_bos
from .doc.bos_api_wrapper import get_sts_dict
from .doc.bos_api_wrapper import get_document_link_string
from .doc.doc_api_wrapper import DocWrapper
from .reader_settings import BUCKET_NAME

import logging
from .log_helper import get_correct_logger
logger = get_correct_logger()


class FileStoreAPI(object):
    """
        provides a interface for storing the file_name and abs_path for a uploaded file.
    """
    def __init__(self, random_time_name):
        abs_path = FileStoreAPI.get_abs_path(random_time_name)
        self.random_time_name = random_time_name
        self.abs_path = abs_path

    def get_file_info_dict(self):
        return {
            "file_name": self.random_time_name,
            "abs_path": self.abs_path,
    }

    @staticmethod
    def get_baidu_file_info_dict_static(dict_obj):

        file_name = dict_obj["file_name"]
        abs_path = get_document_link_string(file_name)

        return {
            "file_name": file_name,
            "abs_path": abs_path,
    }


    @staticmethod
    def get_file_info_dict_static(dict_obj):

        file_name = dict_obj["file_name"]
        abs_path = FileStoreAPI.get_abs_path(file_name)

        return {
            "file_name": file_name,
            "abs_path": abs_path,
    }

    @staticmethod
    def get_abs_path(any_path):
        if not (type(any_path) == str or type(any_path) == unicode):
            logger.error("docreaderxblock FileStoreAPI.get_abs_path receives an non str/unicode argument.")
            raise TypeError("FileStoreAPI.get_system_path receives a non string arg.")
        else:
            file_name = any_path.split("/")[-1]
            abs_path = os.path.join(doc_fs.base_location, file_name)
            if os.path.isfile(abs_path):
                return abs_path
            else:
                logger.error("docreaderxblock FileStoreAPI.get_abs_path file not exists")
                raise OSError("file does not exist.")
    """
    @staticmethod
    def get_abs_path(any_path):
        if not (type(any_path) == str or type(any_path) == unicode):
            logger.error("docreaderxblock FileStoreAPI.get_abs_path receives an non str/unicode argument.")
            raise TypeError("FileStoreAPI.get_system_path receives a non string arg.")
        else:
            file_name = any_path.split("/")[-1]
            abs_path = os.path.join(MEDIA_ROOT, file_name)
            if os.path.isfile(abs_path):
                return abs_path
            else:
                logger.error("docreaderxblock FileStoreAPI.get_abs_path file not exists")
                raise OSError("file does not exist.")
    """
class UploadDownloadAPI(object):

    @staticmethod
    def status_helper(status_json):
        responseDict = json.loads(status_json._container[0])
        file_url = responseDict["result"]["file_url"]
        return file_url

    @staticmethod
    def get_abs_path(file_name_para):
        return os.path.join(MEDIA_ROOT, file_name_para)

    @staticmethod
    def upload(request):
        """
            view that handles file upload via Ajax
        """

        # check upload permission
        error = ''
        new_file_name = ''
        allowed_upload_file_types = ALLOWED_UPLOAD_FILE_TYPE
        max_upload_file_size = MAX_UPLOAD_FILE_SIZE
        try:
            base_file_name = str(time.time()).replace('.', str(random.randint(0, 100000)))
            file_storage, new_file_name = store_uploaded_file(
            request, 'file-upload', allowed_upload_file_types, base_file_name,
            max_file_size=max_upload_file_size
            )
            logger.info(
                "docreaderxblock FileStoreAPI.upload try uploaded {}: success".format(str(new_file_name))
            )
        except Exception as e:
            logger.warning(
                "docreaderxblock FileStoreAPI.upload try uploaded {}: fail -- {}".format(str(new_file_name), e)
            )
            file = request.POST["file-upload"].file
            request.FILES = {}
            request.FILES["file-upload"] = file
            try:
                file_storage, new_file_name = store_uploaded_file(
                    request, 'file-upload', allowed_upload_file_types, base_file_name,
                    max_file_size=max_upload_file_size
                )
                logger.info(
                    "docreaderxblock FileStoreAPI.upload try uploaded {}: success".format(str(new_file_name))
                )
            except Exception as e:
                error = str(type(e)) + " - " + str(e)
                logger.error(
                    "docreaderxblock FileStoreAPI.upload except uploaded {}: fail".format(str(new_file_name), e)
                )
                raise Exception
        if error == '':
            result = 'SUCCESS'
            file_url = file_storage.url(new_file_name)
            parsed_url = urlparse.urlparse(file_url)
            file_url = urlparse.urlunparse(
                urlparse.ParseResult(
                    parsed_url.scheme,
                    parsed_url.netloc,
                    parsed_url.path,
                    '', '', ''
                )
            )
        else:
            result = ''
            file_url = ''

        return HttpResponse(json.dumps({
            'result': {
                'msg': result,
                'error': error,
                'file_url': file_url,
            }
        }), content_type="text/plain")

    @staticmethod
    def download(request, dict_obj):
        BLOCK_SIZE = 8 * 1024
        path = dict_obj["abs_path"]
        try:
            file_descriptor = default_storage.open(path)
            app_iter = iter(partial(file_descriptor.read, BLOCK_SIZE), '')
            return Response(app_iter=app_iter)
        except:
            pass


from .doc.doc_api_wrapper import DocWrapper


class CombinedDocGenerator(DocWrapper):
    """
        The reason why we need this class is that, we need to just get the status for building doc.
    In this case, we just wrap storing doc id into another function
    """
    @staticmethod
    def build_doc_from_bos_bool(self_obj, dict_obj):
        try:
            returned_string = DocWrapper.build_doc_from_bos(dict_obj)
            doc_id_dict = json.loads(returned_string)
            doc_id_dict_reg = {
                "baidu_doc_id": doc_id_dict["documentId"]
            }
            DocReaderXBlockChanger.store_doc_id(self_obj, doc_id_dict_reg)
            return True
        except:
            return False

class DocReaderXBlockChanger(object):

    @staticmethod
    def store_user_upload_info(self_obj, dict_obj):

        allow_download = dict_obj["allow_download"]
        user_defined_name = dict_obj["user_defined_name"]

        self_obj.display_name = user_defined_name
        self_obj.allow_download = allow_download
        self_obj.user_defined_name = user_defined_name

    @staticmethod
    def store_rdtime_names(self_obj, dict_obj):
        file_name = dict_obj["file_name"]
        abs_path  = dict_obj["abs_path"]
        systemGeneratedRandomName = file_name.split(".")[0]
        self_obj.systemGeneratedRandomName = systemGeneratedRandomName
        self_obj.systemGeneratedRandomNameExtension = file_name
        self_obj.systemGeneratedRandomNameAbsPath = abs_path


    @staticmethod
    def store_download_info(self_obj, dict_obj):
        download_link_tea = dict_obj["download_link_tea"]
        self_obj.download_link_tea = download_link_tea

    @staticmethod
    def store_baidu_view_proxy_info(self_obj, dict_obj):
        baidu_view_proxy_url_tea = dict_obj["baidu_view_proxy_url_tea"]
        self_obj.baidu_view_proxy_url_tea = baidu_view_proxy_url_tea


    @staticmethod
    def store_baidu_upload_info(self_obj, dict_obj):
        upload_status = dict_obj["upload_status"]
        bos_status  = dict_obj["bos_status"]
        doc_status = dict_obj["doc_status"]
        self_obj.upload_status = upload_status
        self_obj.bos_status = bos_status
        self_obj.doc_status = doc_status

    @staticmethod
    def store_doc_id(self_obj, dict_obj):
        baidu_doc_id = dict_obj["baidu_doc_id"]
        self_obj.baidu_doc_id = baidu_doc_id

    @staticmethod
    def store_processing_status(self_obj, dict_obj):
        baidu_processing_status = dict_obj["baidu_processing_status"]
        self_obj.baidu_processing_status = baidu_processing_status


class DocReaderXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    """
        The issue here is that, unless we break into class Xblock, else we can only write something inside this framework.
    That is, we cannot use __init__ to initialize instance variables, else there might be a VersionConflict exception.
    
        Another issue is that, the class variables of Scopes, cannot be shared between lms and studio, which means that 
    we need to use a pair of  variables including 
            Tea, 
            Stu
    if we want to change a variable both from lms and studio side. 
    
        For example, here we need to initialize a dynamic variable of the iframe's html, however, since it is dynamic, 
    so for each different block, the address here is not the same. In this case, we need to use a function to grab the 
    value each time we create a new block. This is by given the block a user_settings scope since when we create the xblock, 
        However, when the teacher from studio want to change the value, it becomes impossible.
    
    """

    def get_download_link(self):
        return self.runtime.handler_url(self, "download_proxy")

    def get_baidu_download_link(self):
        return "http://" + self.bucket_name + ".bj.bcebos.com/" + self.systemGeneratedRandomNameExtension

    def get_baidu_view_proxy_link(self):
        return self.runtime.handler_url(self, "baidu_view_proxy")


    bucket_name = String(
         default=BUCKET_NAME, scope=Scope.settings,
         help="name of the bucket"
    )

    countcontent = Integer(
        default=0,
        scope=Scope.content,
        help="total pages",
    )

    countsettings = Integer(
        default=0,
        scope=Scope.settings,
        help="total pages",
    )

    countuser_state = Integer(
        default=0,
        scope=Scope.user_state,
        help="total pages",
    )

    countpreferences = Integer(
        default=0,
        scope=Scope.preferences,
        help="total pages",
    )

    countuser_info = Integer(
        default=0,
        scope=Scope.user_info,
        help="total pages",
    )

    countuser_state_summary = Integer(
        default=0,
        scope=Scope.user_state_summary,
        help="total pages",
    )

    default_upload = Boolean(
        default=True,
        scope=Scope.settings,
        help="name of the LMS address"
    )

    # baidu_view_proxy_url = String(
    #     default="", scope=Scope.settings,
    #     help="name of the LMS address"
    # )

    # baidu_view_proxy_url_stu = String(
    #     default="", scope=Scope.user_state,
    #     help="name of the LMS address"
    # )

    baidu_view_proxy_url_tea = String(
        default="", scope=Scope.settings,
        help="name of the LMS address"
    )

    systemDefaultBaiduId = String(
        default="doc-hmqp85mbqpgfxq5", scope=Scope.settings,
        help="name of the LMS address"
    )

    LMS_ROOT_URL = String(
        default=get_address()["LMS_ROOT_URL"], scope=Scope.settings,
        help="name of the LMS address"
    )

    CMS_ROOT_URL = String(
        default=get_address()["CMS_ROOT_URL"], scope=Scope.settings,
        help="name of the CMS address"
    )

    upload_status = Boolean(
        default=False, scope=Scope.settings,
        help="name of the pdf file"
    )

    bos_status = Boolean(
        default=False, scope=Scope.settings,
        help="name of the pdf file"
    )

    doc_status = Boolean(
        default=False, scope=Scope.settings,
        help="name of the pdf file"
    )

    baidu_doc_id = String(
        default="doc-hmqp85mbqpgfxq5", scope=Scope.settings,
        help="name of the pdf file"
    )

    baidu_processing_status = String(
        default="PUBLISHED", scope=Scope.settings,
        help="name of the pdf file"
    )

    systemGeneratedRandomName = String(
        default="15035435851715194", scope=Scope.settings,
        help="name of the pdf file"
    )

    systemGeneratedRandomNameExtension = String(
        default="15035435851715194", scope=Scope.settings,
        help="name of the pdf file"
    )

    systemGeneratedRandomNameAbsPath = String(
        default="15035435851715194", scope=Scope.settings,
        help="name of the pdf file"
    )

    display_name = String(
        display_name="Display Name",
        default=u"文档预览(新版)",
        scope=Scope.settings,
        help="Name of the component in the edx-platform"
    )

    user_defined_name = String(
        display_name="Display Name",
        default=u"文档预览(新版)",
        scope=Scope.settings,
        help="Name of the component in the edx-platform"
    )

    allow_download = Boolean(display_name=u"允许下载",
                             default=True,
                             scope=Scope.settings,
                             help="Display a download button for this PDF.")

    download_link = String(
        display_name="download_link",
        default=u"http://hmerpf9vp3e2i24ne4a.exp.bcedocument.com/download/doc-hmqp85mbqpgfxq5.pdf?authorization=bce-auth-v1%2F4968510b3d6d42d4971adc2a0a772b48%2F2017-12-28T02%3A34%3A06Z%2F-1%2Fhost%2F47100c720d4b86b922cfe29ee6501e801a7723635a646c5f0fe65fa257a9fd61",
        scope=Scope.settings,
        help="Name of the component in the edx-platform"
    )

    download_link_stu = String(
        display_name="download_link",
        default=u"http://hmerpf9vp3e2i24ne4a.exp.bcedocument.com/download/doc-hmqp85mbqpgfxq5.pdf?authorization=bce-auth-v1%2F4968510b3d6d42d4971adc2a0a772b48%2F2017-12-28T02%3A34%3A06Z%2F-1%2Fhost%2F47100c720d4b86b922cfe29ee6501e801a7723635a646c5f0fe65fa257a9fd61",
        scope=Scope.settings,
        help="Name of the component in the edx-platform"
    )

    download_link_tea = String(
        display_name="download_link",
        default=u"http://hmerpf9vp3e2i24ne4a.exp.bcedocument.com/download/doc-hmqp85mbqpgfxq5.pdf?authorization=bce-auth-v1%2F4968510b3d6d42d4971adc2a0a772b48%2F2017-12-28T02%3A34%3A06Z%2F-1%2Fhost%2F47100c720d4b86b922cfe29ee6501e801a7723635a646c5f0fe65fa257a9fd61",
        scope=Scope.settings,
        help="Name of the component in the edx-platform"
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def render_template(self, htmlPath, context={}):
        """
        Evaluate a template by resource path, applying the provided context
        """
        template_str = pkg_resources.resource_string(__name__, htmlPath)
        return Template(template_str).render(Context(context))

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):

        if self.baidu_view_proxy_url_tea == "":
            has_doc = False
        else:
            has_doc = True

        context = {
            "allow_download": self.allow_download,
            "has_doc": has_doc,
        }

        html = self.render_template('static/html/docreaderxblockStu.html', context=context)
        frag = Fragment(html.format(self=self))

        frag.add_css(self.resource_string("static/css/docreaderxblock.css"))
        frag.add_javascript(self.resource_string(
            "static/js/src/docreaderxblockStu.js"))
        frag.initialize_js('DocReaderXBlock')
        return frag

    def studio_view(self, context=None):
        """
        The primary view of the paellaXBlock, shown to students
        when viewing courses.
        """

        context = {
            "allow_download": self.allow_download,
        }
        html = self.render_template("static/html/docreaderxblockTea.html", context=context)
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/docreaderxblock.css"))
        frag.add_javascript(self.resource_string(
            "static/js/src/docreaderxblockTea.js"))
        frag.initialize_js('DocReaderXBlock')
        return frag

    def baidu_view(self, context=None):
        """
        The primary view of the paellaXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/docreaderxblockBaiduDefault.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/docreaderxblock.css"))
        frag.add_javascript(self.resource_string(
            "static/js/src/docreaderxblockTea.js"))
        frag.initialize_js('DocReaderXBlock')
        return frag

    # in js, we start by getting the firstPage and initialize the total page
    @XBlock.json_handler
    def get_name(self, data, suffix=''):
        return {"systemGeneratedRandomName": self.systemGeneratedRandomName}

    @XBlock.json_handler
    def renewFile(self, data, suffix=''):
        self.systemGeneratedRandomName = data["systemGeneratedRandomName"]
        self.display_name = data["displayName"]
        self.presufFileName = data["presufFileName"]
        self.allow_download = data["allowDownload"]
        # Here need to check how many file are there inside the server
        return {
            "systemGeneratedRandomName": self.systemGeneratedRandomName,
            "displayName": self.display_name,
            "presufFileName": self.presufFileName,
            "allowDownload": self.allow_download,
        }

    @XBlock.json_handler
    def renewName(self, data, suffix=''):
        #print "Here we enter renewName"

        self.display_name = data["user_defined_name"]
        self.user_defined_name = data["user_defined_name"]
        self.allow_download = data["allow_download"]

        # Here need to check how many file are there inside the server
        return {
            "display_name": self.display_name,
            "user_defined_name": self.user_defined_name,
            "allow_download": self.allow_download,
        }

    @XBlock.json_handler
    def touchUpload(self, data, suffix=''):
        return {
            "displayName": 1,
            "allowDownload": 2,
        }

    @XBlock.json_handler
    def check_baidu_upload_status(self, data, suffix=''):

        doc_id_dict = {
            "baidu_doc_id": self.baidu_doc_id,
        }
        baidu_processing_status = DocWrapper.status_by_doc_id(doc_id_dict)


        return {
            "baidu_processing_status": baidu_processing_status,
        }

    @XBlock.json_handler
    def increment_countcontent(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        # Just to show data coming in...
        assert data['hello'] == 'world'
        self.countcontent += 1
        return {"count": 1}

    @XBlock.json_handler
    def increment_countsettings(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        # Just to show data coming in...
        assert data['hello'] == 'world'
        self.countsettings += 1
        return {"count": 1}

    @XBlock.json_handler
    def increment_countuser_state(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        # Just to show data coming in...
        assert data['hello'] == 'world'
        self.countuser_state += 1
        return {"count": 1}

    @XBlock.json_handler
    def increment_countpreferences(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        # Just to show data coming in...
        assert data['hello'] == 'world'
        self.countpreferences += 1
        return {"count": 1}

    @XBlock.json_handler
    def increment_countuser_info(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        # Just to show data coming in...
        assert data['hello'] == 'world'
        self.countuser_info += 1
        return {"count": 1}

    @XBlock.json_handler
    def increment_countuser_state_summary(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        # Just to show data coming in...
        assert data['hello'] == 'world'
        self.countuser_state_summary += 1
        return {"count": 1}


    @XBlock.handler
    def baidu_upload_proxy(self, data, suffix=''):

        # if it can reach this point, then it mean that the file has been successfully uploaded.
        upload_status = False
        bos_status = True
        doc_status = False

        try:
            #1. first we store the info by user
            allow_download = data.POST.get("allow_download")
            user_defined_name = data.POST.get("user_defined_name")
            python_random_name = data.POST.get("python_random_name")

            dict_obj = {
                "user_defined_name": user_defined_name,
                "allow_download": allow_download,
            }
            DocReaderXBlockChanger.store_user_upload_info(self, dict_obj)

            #2. then we store the info of rdtime names
            dict_obj = FileStoreAPI.get_baidu_file_info_dict_static(
                {
                    "file_name": python_random_name,
                })
            DocReaderXBlockChanger.store_rdtime_names(self, dict_obj)

            # 3. we can have a local download handler.
            download_link_tea = self.get_baidu_download_link()
            dict_download_link_tea = {
                "download_link_tea": download_link_tea,
            }
            DocReaderXBlockChanger.store_download_info(self, dict_download_link_tea)

            #4. then we begin to upload to bos.
            if check_file_from_bos(dict_obj) == True:
                # if reach this point, it mean that the file has been successfully uploaded.
                doc_status = CombinedDocGenerator.build_doc_from_bos_bool(self, dict_obj)
            else:
                bos_status = False
        except:
            pass

        #v1
        baidu_view_proxy_url_tea = self.get_baidu_view_proxy_link()
        dict_obj = {
            "baidu_view_proxy_url_tea": baidu_view_proxy_url_tea,
        }
        DocReaderXBlockChanger.store_baidu_view_proxy_info(self, dict_obj)

        # At this point, we've already reached the point whether all requirements are met or not.
        # So we need to store the upload info as well as the user info.
        dict_obj = {
            "upload_status": upload_status,
            "bos_status": bos_status,
            "doc_status": doc_status,
        }
        DocReaderXBlockChanger.store_baidu_upload_info(self, dict_obj)

        doc_id_dict = {
            "baidu_doc_id": self.baidu_doc_id,
        }
        baidu_processing_status = DocWrapper.status_by_doc_id(doc_id_dict)


        status_obj = {
            "baidu_processing_status":baidu_processing_status,
        }
        DocReaderXBlockChanger.store_processing_status(self, status_obj)

        return Response(json_body=dict_obj)

    @XBlock.handler
    def upload_proxy(self, data, suffix=''):

        upload_status = False
        bos_status = False
        doc_status = False

        #1. try upload
        try:
            status = UploadDownloadAPI.upload(data)

            #1. if upload success, then the file will always exists
            if status.status_code == 200:

                upload_status = True

                #1. first we store the info by user
                allow_download = data.POST.get("allow_download")
                user_defined_name = data.POST.get("user_defined_name")

                dict_obj = {
                    "user_defined_name": user_defined_name,
                    "allow_download": allow_download,
                }
                DocReaderXBlockChanger.store_user_upload_info(self, dict_obj)

                #2. then we store the info of rdtime names
                file_url = UploadDownloadAPI.status_helper(status)
                dict_obj = FileStoreAPI.get_file_info_dict_static(
                    {
                        "file_name": file_url,
                    })
                DocReaderXBlockChanger.store_rdtime_names(self, dict_obj)

                # 3. we can have a local download handler.
                download_link_tea = self.get_download_link()
                dict_download_link_tea = {
                    "download_link_tea": download_link_tea,
                }
                DocReaderXBlockChanger.store_download_info(self, dict_download_link_tea)


                #4. then we begin to upload to bos.
                bos_status = upload_file_to_bos(dict_obj)
                if check_file_from_bos(dict_obj) == True:
                    # if reach this point, it mean that the file has been successfully uploaded.
                    bos_status = True
                    doc_status = CombinedDocGenerator.build_doc_from_bos_bool(self, dict_obj)
                else:
                    bos_status = False
            else:
                pass
        except:
            pass

        #v1
        baidu_view_proxy_url_tea = self.get_baidu_view_proxy_link()
        dict_obj = {
            "baidu_view_proxy_url_tea": baidu_view_proxy_url_tea,
        }
        DocReaderXBlockChanger.store_baidu_view_proxy_info(self, dict_obj)

        # At this point, we've already reached the point whether all requirements are met or not.
        # So we need to store the upload info as well as the user info.
        dict_obj = {
            "upload_status": upload_status,
            "bos_status": bos_status,
            "doc_status": doc_status,
        }
        DocReaderXBlockChanger.store_baidu_upload_info(self, dict_obj)

        doc_id_dict = {
            "baidu_doc_id": self.baidu_doc_id,
        }
        baidu_processing_status = DocWrapper.status_by_doc_id(doc_id_dict)


        status_obj = {
            "baidu_processing_status":baidu_processing_status,
        }
        DocReaderXBlockChanger.store_processing_status(self, status_obj)

        return Response(json_body=dict_obj)

    @XBlock.handler
    def full_access_change_proxy(self, data, suffix=''):

        self.countcontent += 1
        self.countpreferences += 1
        self.countsettings += 1
        self.countuser_state += 1
        return Response(json_body={1: 2})

        return None

    @XBlock.handler
    def download_proxy(self, data, suffix=''):
        file_url = self.systemGeneratedRandomNameExtension
        dict_obj = {
            "file_name": file_url,
        }
        dict_obj = FileStoreAPI.get_file_info_dict_static(dict_obj)

        return UploadDownloadAPI.download(data, dict_obj)

    @XBlock.handler
    def baidu_view_proxy(self, data, suffix=''):

        dict_obj = {
            "baidu_doc_id": self.baidu_doc_id,
        }

        baidu_processing_status = DocWrapper.status_by_doc_id(dict_obj)

        if baidu_processing_status == "PUBLISHED":
            status_dict = {
                "baidu_doc_id": self.baidu_doc_id
            }
            html = self.render_template("static/html/docreaderxblockBaidu.html", status_dict)
            return Response(body=html)
        elif baidu_processing_status == "PROCESSING":
            html = self.render_template("static/html/docreaderxblockBaiduProcessing.html")
            return Response(body=html)
        elif baidu_processing_status == "FAILED":
            html = self.render_template("static/html/docreaderxblockBaiduFail.html")
            return Response(body=html)
        else:
            html = self.render_template("static/html/docreaderxblockBaiduFail.html")
            return Response(body=html)

    @XBlock.json_handler
    def get_baidu_sts(self, data, suffix = ''):
        try:
            bucket_name = data["bucket_name"]
        except:
            bucket_name = self.bucket_name
        dict_para = {
            "bucket_name": bucket_name
        }
        return get_sts_dict(dict_para)

    @XBlock.json_handler
    def initiate_address(self, data, suffix=''):
        assert data['hello'] == 'world'
        self.baidu_view_proxy_url_stu = data["baidu_view_proxy_url"]
        return {"baidu_view_proxy_url": self.baidu_view_proxy_url_stu}

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("DocReaderXBlock",
             """<docreaderxblock/>
             """),
            ("Multiple DocReaderXBlock",
             """<vertical_demo>
                <docreaderxblock/>
                <docreaderxblock/>
                <docreaderxblock/>
                </vertical_demo>
             """),
        ]


