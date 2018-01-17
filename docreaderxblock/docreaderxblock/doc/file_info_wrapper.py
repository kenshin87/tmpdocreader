import os

def get_length(file_pointer_para):
    file_pointer_para.seek(0, os.SEEK_END)
    content_length = file_pointer_para.tell()
    file_pointer_para.seek(0)
    return content_length

def get_md5():
    pass
