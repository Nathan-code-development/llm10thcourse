from typing import Any, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlmodel import Session, select

from app.api.deps import get_current_active_user, get_current_teacher_user, get_db
from app.models.submission import Submission, SubmissionRead
from app.models.user import User
from app.services.file_service import save_submission_file, delete_submission_file

router = APIRouter()


@router.post("/", response_model=SubmissionRead)
async def create_submission(
    assignment_id: int = Form(...),
    comments: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    提交作业
    """
    # 检查用户是否是学生
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有学生可以提交作业",
        )
    
    # 保存文件并创建提交记录
    submission = await save_submission_file(
        db=db,
        upload_file=file,
        assignment_id=assignment_id,
        student_id=current_user.id,
        comments=comments,
    )
    
    return submission


@router.get("/", response_model=List[SubmissionRead])
def read_submissions(
    skip: int = 0,
    limit: int = 100,
    assignment_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取提交列表
    """
    query = select(Submission)
    
    # 过滤条件
    if assignment_id:
        query = query.where(Submission.assignment_id == assignment_id)
    
    # 如果是学生，只能查看自己的提交
    if current_user.role == "student":
        query = query.where(Submission.student_id == current_user.id)
    
    # 执行查询
    submissions = db.exec(query.offset(skip).limit(limit)).all()
    return submissions


@router.get("/{submission_id}", response_model=SubmissionRead)
def read_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取提交详情
    """
    submission = db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提交记录不存在",
        )
    
    # 权限检查：只有教师和该提交的学生可以查看
    if current_user.role == "student" and submission.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此提交记录",
        )
    
    return submission


@router.delete("/{submission_id}", response_model=dict)
def delete_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    删除提交
    """
    # 删除文件和提交记录
    delete_submission_file(db, submission_id, current_user.id)
    return {"message": "提交记录已删除"} 