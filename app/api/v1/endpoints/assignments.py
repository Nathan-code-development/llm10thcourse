from typing import Any, List
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlmodel import Session, select

from app.api.deps import get_current_active_user, get_current_teacher_user, get_db
from app.models.assignment import Assignment, AssignmentCreate, AssignmentRead, AssignmentUpdate
from app.models.class_model import ClassMember
from app.models.course import Course
from app.models.user import User
from app.utils import storage
from app.services.notification_service import notify_assignment_created

router = APIRouter()


@router.post("/", response_model=AssignmentRead)
async def create_assignment(
    assignment_in: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_user),
) -> Any:
    """
    创建作业(仅教师)
    """
    # 检查课程是否存在
    course = db.get(Course, assignment_in.course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在",
        )
    
    # 权限检查：只有课程教师和管理员可以创建作业
    if current_user.role != "admin" and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权在此课程创建作业",
        )
    
    # 创建作业
    assignment = Assignment(**assignment_in.dict())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    # 发送通知给班级学生
    notify_assignment_created(
        db=db,
        course_id=course.id,
        assignment_id=assignment.id,
        assignment_title=assignment.title,
    )
    
    return assignment


@router.post("/with-attachment", response_model=AssignmentRead)
async def create_assignment_with_attachment(
    title: str = Form(...),
    description: str = Form(None),
    course_id: int = Form(...),
    due_date: datetime = Form(...),
    total_points: int = Form(100),
    attachment: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_user),
) -> Any:
    """
    创建带附件的作业(仅教师)
    """
    # 检查课程是否存在
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在",
        )
    
    # 权限检查：只有课程教师和管理员可以创建作业
    if current_user.role != "admin" and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权在此课程创建作业",
        )
    
    # 保存附件
    file_path = storage.save_upload_file(attachment, folder=f"courses/{course_id}/assignments")
    attachment_url = storage.get_file_url(file_path)
    
    # 创建作业
    assignment = Assignment(
        title=title,
        description=description,
        course_id=course_id,
        due_date=due_date,
        total_points=total_points,
        attachment_url=attachment_url,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    # 发送通知给班级学生
    notify_assignment_created(
        db=db,
        course_id=course.id,
        assignment_id=assignment.id,
        assignment_title=assignment.title,
    )
    
    return assignment


@router.get("/", response_model=List[AssignmentRead])
def read_assignments(
    skip: int = 0,
    limit: int = 100,
    course_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取作业列表
    """
    query = select(Assignment)
    
    # 过滤条件
    if course_id:
        query = query.where(Assignment.course_id == course_id)
    
    # 如果不是管理员，只能查看自己所在班级的课程的作业
    if current_user.role != "admin":
        # 获取用户所在的班级
        class_members = db.exec(
            select(ClassMember).where(ClassMember.user_id == current_user.id)
        ).all()
        class_ids = [cm.class_id for cm in class_members]
        
        # 获取用户所在班级的课程
        courses = db.exec(
            select(Course).where(Course.class_id.in_(class_ids))
        ).all()
        course_ids = [c.id for c in courses]
        
        # 如果没有指定课程ID，则查询所有所在班级的课程的作业
        if not course_id:
            if not course_ids:  # 如果用户不在任何班级的课程中
                return []
            query = query.where(Assignment.course_id.in_(course_ids))
        # 如果指定了课程ID，则检查用户是否有权限查看
        elif course_id not in course_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此课程的作业",
            )
    
    # 执行查询
    assignments = db.exec(query.offset(skip).limit(limit)).all()
    return assignments


@router.get("/{assignment_id}", response_model=AssignmentRead)
def read_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取作业详情
    """
    # 查询作业
    assignment = db.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作业不存在",
        )
    
    # 获取课程和班级信息
    course = db.get(Course, assignment.course_id)
    
    # 权限检查：管理员可以查看所有作业，其他人只能查看自己所在班级的课程的作业
    if current_user.role != "admin":
        is_member = db.exec(
            select(ClassMember).where(
                ClassMember.class_id == course.class_id,
                ClassMember.user_id == current_user.id,
            )
        ).first()
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此作业",
            )
    
    return assignment


@router.put("/{assignment_id}", response_model=AssignmentRead)
def update_assignment(
    assignment_id: int,
    assignment_in: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_user),
) -> Any:
    """
    更新作业信息(仅教师)
    """
    # 查询作业
    assignment = db.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作业不存在",
        )
    
    # 获取课程信息
    course = db.get(Course, assignment.course_id)
    
    # 权限检查：只有课程教师和管理员可以更新作业
    if current_user.role != "admin" and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新此作业",
        )
    
    # 更新作业信息
    assignment_data = assignment_in.dict(exclude_unset=True)
    for key, value in assignment_data.items():
        setattr(assignment, key, value)
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return assignment


@router.delete("/{assignment_id}", response_model=dict)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_user),
) -> Any:
    """
    删除作业(仅教师)
    """
    # 查询作业
    assignment = db.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作业不存在",
        )
    
    # 获取课程信息
    course = db.get(Course, assignment.course_id)
    
    # 权限检查：只有课程教师和管理员可以删除作业
    if current_user.role != "admin" and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此作业",
        )
    
    # 删除附件文件
    if assignment.attachment_url:
        file_path = assignment.attachment_url.replace("/uploads/", "")
        storage.delete_file(file_path)
    
    # 删除作业
    db.delete(assignment)
    db.commit()
    
    return {"message": "作业已删除"}


@router.get("/course/{course_id}", response_model=List[AssignmentRead])
def read_course_assignments(
    course_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取课程的作业列表
    """
    # 查询课程
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在",
        )
    
    # 权限检查：管理员可以查看所有作业，其他人只能查看自己所在班级的课程的作业
    if current_user.role != "admin":
        is_member = db.exec(
            select(ClassMember).where(
                ClassMember.class_id == course.class_id,
                ClassMember.user_id == current_user.id,
            )
        ).first()
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此课程的作业",
            )
    
    # 获取课程作业列表
    assignments = db.exec(
        select(Assignment)
        .where(Assignment.course_id == course_id)
        .offset(skip)
        .limit(limit)
    ).all()
    
    return assignments 