import os
import shutil
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


def get_storage_path() -> Path:
    """
    获取存储路径
    """
    storage_path = Path(settings.LOCAL_STORAGE_PATH)
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


def save_upload_file(upload_file: UploadFile, folder: str = "") -> str:
    """
    保存上传文件到本地存储
    
    Args:
        upload_file: 上传的文件
        folder: 子文件夹名称
        
    Returns:
        文件的URL路径
    """
    if settings.STORAGE_TYPE == "local":
        return save_local_file(upload_file, folder)
    elif settings.STORAGE_TYPE == "s3":
        # TODO: 实现S3存储
        raise NotImplementedError("S3存储未实现")
    elif settings.STORAGE_TYPE == "aliyun":
        # TODO: 实现阿里云OSS存储
        raise NotImplementedError("阿里云OSS存储未实现")
    else:
        raise ValueError(f"不支持的存储类型: {settings.STORAGE_TYPE}")


def save_local_file(upload_file: UploadFile, folder: str = "") -> str:
    """
    保存文件到本地存储
    """
    # 获取文件名和扩展名
    filename = upload_file.filename
    if not filename:
        file_ext = ".bin"
    else:
        file_ext = os.path.splitext(filename)[1]
        
    # 生成唯一文件名
    unique_filename = f"{uuid4().hex}{file_ext}"
    
    # 构建目标路径
    storage_path = get_storage_path()
    destination_folder = storage_path / folder if folder else storage_path
    destination_folder.mkdir(parents=True, exist_ok=True)
    destination_path = destination_folder / unique_filename
    
    # 保存文件
    with destination_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    # 返回文件URL (相对路径)
    relative_path = os.path.join(folder, unique_filename) if folder else unique_filename
    return relative_path


def get_file_url(file_path: str) -> str:
    """
    获取文件的完整URL
    """
    if settings.STORAGE_TYPE == "local":
        return f"/uploads/{file_path}"
    else:
        # 其他存储类型，如S3或阿里云OSS，应该返回完整URL
        return file_path


def delete_file(file_path: str) -> bool:
    """
    删除文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否删除成功
    """
    if settings.STORAGE_TYPE == "local":
        storage_path = get_storage_path()
        file_to_delete = storage_path / file_path
        
        if file_to_delete.exists():
            file_to_delete.unlink()
            return True
        return False
    else:
        # TODO: 实现其他存储类型的文件删除
        raise NotImplementedError(f"{settings.STORAGE_TYPE}存储的文件删除未实现") 