from django.conf import settings
import logging
import sys

"""
    We use the settings.LMS_ROOT_URL variable to define the logger here. 
    Depend on the settings, it can write to either:
        /edx/var/log/cms/edx.log, or
        docreaderxblock.log
"""

try:
    status = settings.LMS_ROOT_URL
except AttributeError:
    logging_config = {
        "level": logging.INFO,
        "stream": sys.stdout,
    }
    logging.basicConfig(**logging_config)

def get_correct_logger():
    return logging.getLogger(__name__)
