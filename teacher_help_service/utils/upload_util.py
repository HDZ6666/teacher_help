import os
import random
from datetime import datetime
from fastapi import UploadFile
from config.env import UploadConfig


class UploadUtil:
    """
    上传工具类
    """

    @classmethod
    def generate_random_number(cls):
        """
        生成3位数字构成的字符串

        :return: 3位数字构成的字符串
        """
        random_number = random.randint(1, 999)

        return f'{random_number:03}'

    @classmethod
    def check_file_exists(cls, filepath: str):
        """
        检查文件是否存在

        :param filepath: 文件路径
        :return: 校验结果
        """
        return os.path.exists(filepath)

    @classmethod
    def check_file_extension(cls, file: UploadFile):
        """
        检查文件后缀是否合法

        :param file: 文件对象
        :return: 校验结果
        """
        if not file.filename or '.' not in file.filename:
            return False
        file_extension = cls.get_file_extension(file.filename)
        if file_extension in UploadConfig.DEFAULT_ALLOWED_EXTENSION:
            return True
        return False

    @classmethod
    def get_file_extension(cls, filename: str):
        """
        获取文件后缀（小写）

        :param filename: 文件名称
        :return: 文件后缀
        """
        return os.path.basename(filename or '').rsplit('.', 1)[-1].lower()

    @classmethod
    def resolve_safe_path(cls, base_dir: str, file_name: str):
        """
        将相对文件名解析为基础目录下的真实路径，拒绝绝对路径和越出基础目录的路径

        :param base_dir: 基础目录
        :param file_name: 相对文件名
        :return: 合法时返回真实路径，否则返回None
        """
        if not file_name or '\x00' in file_name:
            return None
        if os.path.isabs(file_name) or file_name.startswith(('/', '\\')) or os.path.splitdrive(file_name)[0]:
            return None
        base_real_path = os.path.realpath(base_dir)
        target_real_path = os.path.realpath(os.path.join(base_real_path, file_name))
        if (
            os.path.commonpath([base_real_path, target_real_path]) != base_real_path
            or target_real_path == base_real_path
        ):
            return None
        return target_real_path

    @classmethod
    def check_file_timestamp(cls, filename: str):
        """
        校验文件时间戳是否合法

        :param filename: 文件名称
        :return: 校验结果
        """
        timestamp = filename.rsplit('.', 1)[0].split('_')[-1].split(UploadConfig.UPLOAD_MACHINE)[0]
        try:
            datetime.strptime(timestamp, '%Y%m%d%H%M%S')
            return True
        except ValueError:
            return False

    @classmethod
    def check_file_machine(cls, filename: str):
        """
        校验文件机器码是否合法

        :param filename: 文件名称
        :return: 校验结果
        """
        if filename.rsplit('.', 1)[0][-4] == UploadConfig.UPLOAD_MACHINE:
            return True
        return False

    @classmethod
    def check_file_random_code(cls, filename: str):
        """
        校验文件随机码是否合法

        :param filename: 文件名称
        :return: 校验结果
        """
        valid_code_list = [f'{i:03}' for i in range(1, 999)]
        if filename.rsplit('.', 1)[0][-3:] in valid_code_list:
            return True
        return False

    @classmethod
    def generate_file(cls, filepath: str):
        """
        根据文件生成二进制数据

        :param filepath: 文件路径
        :yield: 二进制数据
        """
        with open(filepath, 'rb') as response_file:
            yield from response_file

    @classmethod
    def delete_file(cls, filepath: str):
        """
        根据文件路径删除对应文件

        :param filepath: 文件路径
        """
        os.remove(filepath)
