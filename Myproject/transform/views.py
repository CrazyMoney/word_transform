import os


from django_redis import get_redis_connection
from django.http import HttpResponse, FileResponse, JsonResponse
from django.shortcuts import render
from django.views import View

from transform.models import TransformTask
from transform.tasks import transform, transform_local
from celery.result import AsyncResult
import uuid


class IndexView(View):
    # 首頁
    def get(self, request):
        all_task =  TransformTask.objects.all()
        task_dir = {}
        for task in all_task:
            task_dir[task.id] = task.name
        content = task_dir
        print(task_dir)
        return render(request, 'local.html',context = content)



class Ask_status(View):
    # 通过celery 任务的id获取任务的执行状态
    def get(self, request, task_id):
        import logging

        logger = logging.getLogger('mylog')

        if task_id:
            async_task = AsyncResult(id=task_id, app=transform)
            if async_task.status == 'SUCCESS':  # celery 的task完成转换 将返回路径保持在Redis中

                file_path = async_task.get(propagate=False)
                UUID = str(uuid.uuid1())
                try:
                    # file_obj = FilePath.objects.get(file_path = file_path,is_delete= False)
                    redis_con = get_redis_connection("FilePath")
                    redis_con.set(UUID, file_path, ex=60 * 60 * 8)  # 设置过期时间8小时
                except:
                    result = {
                        "success": False,
                        'uu_id': '保存文件失败',
                    }
                    return JsonResponse(status=200, data=result)
                result = {
                    "success": True,
                    'uui': UUID,
                }
                return JsonResponse(status=200, data=result)
            else:
                result = {
                    'success': False,
                    'uui': 'Not ok',
                }
                return JsonResponse(status=200, data=result)
        else:

            return HttpResponse(status=400)






class TransformLocalView(View):

    def get(self, request, transform_id, parameter):
        # 执行dir查询命令
        transformer = TransformTask.objects.get(id=transform_id)
        excute_path = transformer.excute_path
        command = transformer.command
        save_path = transformer.save_path
        default_parameter = transformer.default_parameter
        file_path = ''
        name = ''
        transformer_id = transformer.id

        # 执行celery任务
        task = transform_local.delay(
                                    excute_path=excute_path,
                                    command=command,
                                    save_path=save_path,
                                    parameter=parameter,
                                    default_parameter=default_parameter,
                                    file_path=file_path,
                                    name=name,
                                    transformer_id=transformer_id,
                                    )

        data1 = {
                'success': True,
                'task_id': task.id,
                'file_name': 'result'
                 }
        return JsonResponse(status=200, data=data1)


    def post(self, request, transform_id, parameter):
        # 文档转换
        transformer = TransformTask.objects.get(id=transform_id)
        excute_path = transformer.excute_path
        command = transformer.command
        save_path = transformer.save_path
        default_parameter = transformer.default_parameter
        transformer_id = transformer.id
        upload_file  = transformer.upload_file
        if upload_file:
            myfile = request.FILES.get('file')

            # 接收文件並保存
            if myfile:
                file_name = myfile.name
                name = file_name.split('.docx')[0]
                file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/storage_pack/' + file_name
                with open(file_path, 'wb+') as document:
                    for chunk in myfile.chunks():
                        document.write(chunk)
                document.close()

                # 启动celery文档转换任务
                task = transform_local.delay(excute_path=excute_path,
                                             command=command,
                                             file_path=file_path,
                                             save_path=save_path,
                                             parameter=parameter,
                                             name=name,
                                             default_parameter=default_parameter,
                                             transformer_id=transformer_id,
                                             )

                data1 = {
                        'success': True,
                        'task_id': task.id,
                        'file_name': name,
                        }

                return JsonResponse(status=200, data=data1)
            else:
                return HttpResponse('打开文件失败')
        else:
            file_path = ''
            name = ''
            transformer_id = transformer.id

            # 执行celery任务
            task = transform_local.delay(
                excute_path=excute_path,
                command=command,
                save_path=save_path,
                parameter=parameter,
                default_parameter=default_parameter,
                file_path=file_path,
                name=name,
                transformer_id=transformer_id,
            )

            data1 = {
                'success': True,
                'task_id': task.id,
                'file_name': 'result'
            }
            return JsonResponse(status=200, data=data1)




class GetSaveFile(View):
    # 文檔下載接口
    def get(self, request):
        # 根据客户的UUID获取相应文件的存储地址
        #'info:',errmsg,'file_path:', save_path
        UUID = request.GET.get('UUID')
        red_conn = get_redis_connection("FilePath")
        file_path = red_conn.get(UUID)
        file_path = file_path.decode('utf-8')
        file_list = file_path.split('file_path:')
        infor = file_list[0]
        print('infor',infor)
        file_path = file_list[-1]
        print('file_path',file_path)

        file_path = file_path.strip()
        file_path = file_path.replace('\r\n', '')
        errmsg = infor.split('info:')
        print('errmsg', errmsg)

        errmsg   = errmsg[-1].strip()
        errmsg = errmsg.replace('\r\n', '')

        if errmsg != '':
            # 判断是否存在报错
#TODO
            with open(file_path, 'w') as f:
                # 将错误信息写入文档
                f.write(errmsg)
            f.close()

            stream = open(file_path, 'rb')
            # 將錯誤信息發送給前端
            return FileResponse(stream,
                                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        else:

            # 返回转换后的文档
            steam = open(file_path, 'rb')
            return FileResponse(steam,
                                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
