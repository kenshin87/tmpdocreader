import os
import logging
from django.core.files.storage import FileSystemStorage


from .log_helper import get_correct_logger
from django.conf import settings
from django.core.urlresolvers import reverse

logger = get_correct_logger()


ALLOWED_UPLOAD_FILE_TYPE = [
    #'.gif',
     #'.png',
     #'.jpg',
     #'.bmp',
     #'.jpeg',
     '.doc',
     '.docx',
     '.ppt',
     '.pptx',
     '.xls',
     '.xlsx',
     '.pdf',
     #'.zip',
     #'.rar',
]

MAX_UPLOAD_FILE_SIZE = 1024 * 1024 * 100

"""
    set the MEDIA_ROOT variable here.
        1. If settings.MEDIA_ROOT is correct, then check and return
        2. else, we set the media_root as root.
"""

try:
    MEDIA_ROOT = settings.MEDIA_ROOT
    logger.info("docreaderxblock has the default of: " + MEDIA_ROOT)
except:
    logger.error("settings doesn't have the attribute of settings.MEDIA_ROOT")
    MEDIA_ROOT = ""

if MEDIA_ROOT == "" or MEDIA_ROOT is None:
    media_prefix = os.getcwd()
    media_suffix = "all_files"
    MEDIA_ROOT = os.path.join(media_prefix, media_suffix)

if os.path.isdir(MEDIA_ROOT):
    pass
else:
    try:
        os.makedirs(MEDIA_ROOT)
        os.info("docreaderxblock makedirs of {}".format(MEDIA_ROOT))
    except:
        logger.error("docreaderxblock cannot makedirs for {}".format(MEDIA_ROOT))


doc_storage = "docFiles"
doc_fs = FileSystemStorage(os.path.join(MEDIA_ROOT, doc_storage))

BUCKET_NAME = "testing-yingli"







def get_address():
    address_dict = {}
    address_dict["LMS_ROOT_URL"] = getattr(settings, "LMS_ROOT_URL", None)
    address_dict["CMS_ROOT_URL"] = getattr(settings, "CMS_ROOT_URL", None)
    return address_dict


def reverse_wrapper(dict_para):

    handler = dict_para["handler"]
    usage_key_string = dict_para["usage_key_string"]

    correct_dict = {
        "handler":handler,
        "usage_key_string":usage_key_string,
    }

    try:
        settings.LMS_ROOT_URL
        return reverse("component_handler", correct_dict)
    except:
        return reverse("handler", correct_dict)
