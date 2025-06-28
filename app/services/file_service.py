from fastapi import UploadFile, HTTPException
from sqlmodel import Session, select

from app.models.submission import Submission
from app.utils import storage


async def save_submission_file(
    db: Session, 
    upload_file: UploadFile,
    assignment_id: int,
    student_id: int,
    comments: str = None
) -> Submission:
    """
    保存提交的作业文件
    
    Args:
        db: 数据库会话
        upload_file: 上传的文件
        assignment_id: 作业ID
        student_id: 学生ID
        comments: 提交备注
        
    Returns:
        创建的提交记录
    """
    # 检查文件类型
    allowed_content_types = [
        "application/pdf",
        "application/msword", 
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "text/plain",
        "image/jpeg",
        "image/png",
        "application/zip",
        "application/x-rar-compressed"
    ]
    
    if upload_file.content_type not in allowed_content_types:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    # 保存文件
    file_path = storage.save_upload_file(upload_file, folder=f"assignments/{assignment_id}")
    file_url = storage.get_file_url(file_path)
    
    # 创建提交记录
    submission = Submission(
        assignment_id=assignment_id,
        student_id=student_id,
        file_url=file_url,
        comments=comments
    )
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    return submission


def delete_submission_file(db: Session, submission_id: int, user_id: int) -> bool:
    """
    删除提交的作业文件
    
    Args:
        db: 数据库会话
        submission_id: 提交ID
        user_id: 当前用户ID (用于权限检查)
        
    Returns:
        是否删除成功
    """
    # 查找提交记录
    submission = db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="提交记录不存在")
    
    # 检查权限
    if submission.student_id != user_id:
        raise HTTPException(status_code=403, detail="无权删除此文件")
    
    # 从文件系统中删除文件
    file_path = submission.file_url.replace("/uploads/", "")
    deleted = storage.delete_file(file_path)
    
    # 从数据库中删除记录
    db.delete(submission)
    db.commit()
    
    return deleted 