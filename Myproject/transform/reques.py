import requests
from requests_toolbelt import MultipartEncoder


def get_resposnse():
    url = 'http://127.0.0.1:9000/change/'
    file_path = '/Users/zheng/Desktop/work-master/Myproject/storage_pack/表色测试.docx'

    m = MultipartEncoder(
        fields={'Content-Type': 'multipart/form-data',
                'file': ('file', open(file_path, 'rb'))}
    )

    print('=======start ====')
    r = requests.post(url=url, data =m, headers={'Content-Type': m.content_type})



    return r.content

r = get_resposnse()
file_save ='/Users/zheng/Desktop/work-master/Myproject/storage_pack/save.docx'
with open(file_save,'wb+') as f:
    f.write(r)
f.close()

# print(r)
from threading import  Lock
