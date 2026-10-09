import os
import uuid
from datetime import datetime
from fastapi import BackgroundTasks, Request, UploadFile
from config.env import UploadConfig
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel, UploadResponseModel
from utils.upload_util import UploadUtil


class CommonService:
    """
    通用模块服务层
    """

    @classmethod
    async def upload_service(cls, request: Request, file: UploadFile):
        """
        通用上传service

        :param request: Request对象
        :param file: 上传文件对象
        :return: 上传结果
        """
        if not UploadUtil.check_file_extension(file):
            raise ServiceException(message='文件类型不合法')
        else:
            now = datetime.now()
            relative_path = f'upload/{now.strftime("%Y")}/{now.strftime("%m")}/{now.strftime("%d")}'
            dir_path = os.path.join(UploadConfig.UPLOAD_PATH, relative_path)
            os.makedirs(dir_path, exist_ok=True)
            # 文件名由服务端生成，不使用客户端传入的文件名，避免路径穿越
            file_extension = UploadUtil.get_file_extension(file.filename)
            filename = (
                f'{uuid.uuid4().hex[:8]}_{now.strftime("%Y%m%d%H%M%S")}'
                f'{UploadConfig.UPLOAD_MACHINE}{UploadUtil.generate_random_number()}.{file_extension}'
            )
            filepath = os.path.join(dir_path, filename)
            written_size = 0
            try:
                with open(filepath, 'wb') as f:
                    # 流式写出文件，每次读取1MB，超过大小上限立即中止
                    for chunk in iter(lambda: file.file.read(1024 * 1024), b''):
                        written_size += len(chunk)
                        if written_size > UploadConfig.UPLOAD_MAX_SIZE:
                            raise ServiceException(
                                message=f'文件大小不能超过{UploadConfig.UPLOAD_MAX_SIZE // (1024 * 1024)}MB'
                            )
                        f.write(chunk)
            except ServiceException:
                if os.path.exists(filepath):
                    os.remove(filepath)
                raise

            return CrudResponseModel(
                is_success=True,
                result=UploadResponseModel(
                    fileName=f'{UploadConfig.UPLOAD_PREFIX}/{relative_path}/{filename}',
                    newFileName=filename,
                    originalFilename=file.filename,
                    url=f'{request.base_url}{UploadConfig.UPLOAD_PREFIX[1:]}/{relative_path}/{filename}',
                ),
                message='上传成功',
            )

    @classmethod
    async def download_services(cls, background_tasks: BackgroundTasks, file_name, delete: bool):
        """
        下载下载目录文件service

        :param background_tasks: 后台任务对象
        :param file_name: 下载的文件名称
        :param delete: 是否在下载完成后删除文件
        :return: 上传结果
        """
        filepath = UploadUtil.resolve_safe_path(UploadConfig.DOWNLOAD_PATH, file_name)
        if not filepath:
            raise ServiceException(message='文件名称不合法')
        elif not os.path.isfile(filepath):
            raise ServiceException(message='文件不存在')
        else:
            if delete:
                background_tasks.add_task(UploadUtil.delete_file, filepath)
            return CrudResponseModel(is_success=True, result=UploadUtil.generate_file(filepath), message='下载成功')

    @classmethod
    async def download_resource_services(cls, resource: str):
        """
        下载上传目录文件service

        :param resource: 下载的文件名称
        :return: 上传结果
        """
        if not resource.startswith(f'{UploadConfig.UPLOAD_PREFIX}/'):
            raise ServiceException(message='文件名称不合法')
        filepath = UploadUtil.resolve_safe_path(
            UploadConfig.UPLOAD_PATH, resource[len(UploadConfig.UPLOAD_PREFIX) + 1 :]
        )
        filename = resource.rsplit('/', 1)[-1]
        if (
            not filepath
            or not UploadUtil.check_file_timestamp(filename)
            or not UploadUtil.check_file_machine(filename)
            or not UploadUtil.check_file_random_code(filename)
        ):
            raise ServiceException(message='文件名称不合法')
        elif not os.path.isfile(filepath):
            raise ServiceException(message='文件不存在')
        else:
            return CrudResponseModel(is_success=True, result=UploadUtil.generate_file(filepath), message='下载成功')
