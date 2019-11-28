

from django.db import models



class TransformTask(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name= '任务id')
    name = models.CharField(max_length= 50)
    default_parameter = models.CharField(max_length= 100,null=True, verbose_name='任务参数')
    command =  models.CharField(max_length=50, null=True, verbose_name='执行程序命令')
    excute_path = models.CharField(max_length=100,null=True, verbose_name='可执行程序路径')
    save_path = models.CharField(max_length=100,null=True,verbose_name='文件存储位置')
    upload_file  = models.BooleanField(verbose_name='是否需要上传文档',default=False)

    class Meta:
        db_table = 'tb_task'
        verbose_name = '任务'



class FilePath(models.Model):
    id = models.IntegerField(primary_key=True,verbose_name='文件ID')
    name = models.CharField(max_length=50,unique=True)
    file_path = models.CharField(max_length=100,unique=True)
    is_delete  = models.BooleanField(default=False)
    transform = models.ForeignKey('TransformTask', related_name ='file_task',on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'tb_filepath'
        verbose_name = '文件路径'


