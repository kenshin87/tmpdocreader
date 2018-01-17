import os
import unittest
from .test_base import TestBase
from .request_helper import request_send_file_local


from django.test.client import RequestFactory
from django.test.client import Client

from docreaderxblock.docreaderxblock import UploadDownloadAPI



def dictToRequestByFactory(dictPara):
    """
        This is an alternative request generator, in case of the client one failing to work.
    """
    instanceOfRequestFactory = RequestFactory()
    request = instanceOfRequestFactory.get("8000")
    return request


class TestUploadDownloadAPI(TestBase):
    def set_up(self):
        pass

#from docreaderxblock.docreaderxblock.tests.test_docreaderxblock import TestFileStoreAPI
class TestFileStoreAPI(TestBase):

    def set_up(self, default=None):

        client = Client()
        response = client.get("8000")
        request = response.wsgi_request

        self.request = request

        current_path = os.getcwd()
        abs_path = os.path.join(current_path, "test_path")
        existed_path = abs_path + "/t.pdf"
        if os.path.isfile(existed_path):
            return True
        else:
            try:
                os.makedirs(abs_path)
                command = "echo tester>>{}"
                path_pdf = abs_path + "/t.pdf"
                os.system(command.format(path_pdf))
                path_ppt = abs_path + "/t.ppt"
                os.system(command.format(path_ppt))
                path_xls =\
                    abs_path + "/t.xls"
                os.system(command.format(path_xls))
                path_doc = abs_path + "/t.doc"
                os.system(command.format(path_doc))
                path_false = abs_path + "/t.false"
                os.system(command.format(path_false))
                return True
            except:
                return False
    def test_upload_file(self):





    def runTest(self):
        pass
