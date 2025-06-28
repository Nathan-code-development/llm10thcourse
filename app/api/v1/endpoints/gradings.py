from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_active_user, get_current_teacher_user, get_db
from app.models.grading import Grading, GradingCreate, GradingRead, GradingUpdate
from app.models.submission import Submission, SubmissionStatus
from app.models.user import User
from app.services.notification_service import notify_grading_completed

router = APIRouter()


@router.post("/", response_model=GradingRead)
def create_grading(
    grading_in: GradingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_user),
) -> Any:
    """
    批改作业
    """
    # 检查提交记录是否存在
    submission = db.get(Submission, grading_in.submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提交记录不存在",
        )
    
    # 检查提交记录是否已被批改
    existing_grading = db.exec(
        select(Grading).where(Grading.submission_id == grading_in.submission_id)
    ).first()
    if existing_grading:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该提交记录已被批改",
        )
    
    # 检查分数是否在有效范围内
    assignment = submission.assignment
    if grading_in.score < 0 or grading_in.score > assignment.total_points:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"分数必须在0到{assignment.total_points}之间",
        )
    
    # 创建批改记录
    grading = Grading(
        **grading_in.dict(),
        teacher_id=current_user.id,
    )
    db.add(grading)
    
    # 更新提交记录状态
    submission.status = SubmissionStatus.GRADED
    
    db.commit()
    db.refresh(grading)
    
    # 发送通知给学生
    notify_grading_completed(
        db=db,
        submission_id=submission.id,
        assignment_title=assignment.title,
        score=grading.score,
    )
    
    return grading


@router.get("/{grading_id}", response_model=GradingRead)
def read_grading(
    grading_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取批改详情
    """
    grading = db.get(Grading, grading_id)
    if not grading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批改记录不存在",
        )
    
    # 权限检查：只有教师和该提交的学生可以查看
    submission = db.get(Submission, grading.submission_id)
    if current_user.role == "student" and submission.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此批改记录",
        )
    
    return grading


@router.put("/{grading_id}", response_model=GradingRead)
def update_grading(
    grading_id: int,
    grading_in: GradingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_user),
) -> Any:
    """
    更新批改信息
    """
    grading = db.get(Grading, grading_id)
    if not grading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批改记录不存在",
        )
    
    # 权限检查：只有批改老师可以更新
    if grading.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新此批改记录",
        )
    
    # 更新批改记录
    grading_data = grading_in.dict(exclude_unset=True)
    for key, value in grading_data.items():
        setattr(grading, key, value)
    
    db.add(grading)
    db.commit()
    db.refresh(grading)
    
    return grading


@router.get("/submission/{submission_id}", response_model=GradingRead)
def read_submission_grading(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取提交的批改
    """
    # 检查提交记录是否存在
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
            detail="无权查看此批改记录",
        )
    
    # 获取批改记录
    grading = db.exec(
        select(Grading).where(Grading.submission_id == submission_id)
    ).first()
    if not grading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批改记录不存在",
        )
    
    return grading 