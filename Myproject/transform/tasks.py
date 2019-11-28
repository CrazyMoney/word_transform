# Create your tasks here
from __future__ import absolute_import, unicode_literals

import os
import string
import  subprocess
import requests
from celery import shared_task
from requests_toolbelt import MultipartEncoder


@shared_task
def transform():
    #远程调用命令
        url = 'http://127.0.0.1:9000/change/'
        file_path = 'E://zhengguoliang//home-master//Myproject//storage_pack//格着色测试.docx'

        m = MultipartEncoder(
            fields={'Content-Type': 'multipart/form-data',
                    'file': ('表格着试.docx', open(file_path, 'rb'))}
        )
        r = requests.post(url=url, data=m, headers={'Content-Type': m.content_type})
        print(r.text)
        return r.text




#
# @shared_task
# def transform():
#     #远程调用命令
#         url = 'http://127.0.0.1:9000/change/'
#         file_path = 'E://zhengguoliang//home-master//Myproject//storage_pack//格着色测试.docx'
#
#         m = MultipartEncoder(
#             fields={'Content-Type': 'multipart/form-data',
#                     'file': ('表格着试.docx', open(file_path, 'rb'))}
#         )
#         r = requests.post(url=url, data=m, headers={'Content-Type': m.content_type})
#         print(r.text)
#         return r.text

def get_disklist():
    # 获取系统所有盘符
    disk_list = []
    for c in string.ascii_uppercase:
        disk = c + ':'
        if os.path.isdir(disk):
            disk_list.append(disk)
    return disk_list

# def get_exe_path():
#     # 获取exe执行文件路径
#     exe_list = []
#     dir_list = get_disklist()
#     for dir in dir_list:
#         os.chdir(dir)
#         # find_str = 'for /r E: %i in (makeup_for_word.*) do @echo %i'
#         find_exe = 'for /r ' + dir + ' %i in (makeup_for_word_locla.*) do @echo %i'
#         print(find_exe)
#
#         # result = os.popen(find_exe)
#         # result = result.read().encode('utf-8').decode('utf-8').split('\n')
#
#         result = subprocess.getoutput(find_exe)
#         result = result.encode('utf-8').decode('utf-8').split('\n')
#         print('result', result)
#         exe_list.append(result)
#     print('exeLIst', exe_list)
#     exe_excutepath ='E://zhengguoliang//dist//makeup_for_word_locla.exe' #在celery中无法找到除c盘以外的程序
#
#     for path in exe_list:
#         for exe_path in path:
#             if exe_path.endswith('makeup_for_word_locla.exe'):
#                 exe_excutepath = exe_path
#     print('bbbbb', exe_excutepath)
#     return exe_excutepath




@shared_task
def transform_local(**kwargs):
    #调用本地应用
    excute_path= kwargs['excute_path']
    command = kwargs['command']
    file_path = kwargs['file_path']
    save_path= kwargs['save_path']
    name= kwargs['name']
    default_parameter = kwargs['default_parameter']
    parameter = kwargs['parameter']
    transformer_id = kwargs['transformer_id']

    if parameter!='undefined': #客戶定義的參數
        command = command + ' ' + parameter

    if len(default_parameter.strip())!= 0: #命令執行的默認參數
        command = command + ' ' + default_parameter

    if len(excute_path.strip())!= 0:  #執行文件所在目錄
        os.chdir( excute_path)

    if      len(file_path.strip())!= 0 and transformer_id == 1:# word表格著色自動著色任務
            p = subprocess.Popen(command,
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE,shell=True)
            path = file_path+';'+save_path+';'+name
            path = bytes(path, encoding='utf8')
            stdout, stderr = p.communicate(input=path+b'\n')  #运行exe并自动输入参数
            print(stdout.decode('utf8'))
            return stdout.decode('utf8')
    elif    transformer_id ==2 :    # ls返回項目目錄的任務
                os.system(command + ' ' + save_path,)
                return  "file_path:" + save_path
    else: #其他接口
        pass





