from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_active_user, get_current_teacher_user, get_db
from app.models.class_model import Class, ClassMember
from app.models.course import Course, CourseCreate, CourseRead, CourseUpdate
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=CourseRead)
def create_course(
    course_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_user),
) -> Any:
    """
    创建课程(仅教师)
    """
    # 检查班级是否存在
    class_ = db.get(Class, course_in.class_id)
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在",
        )
    
    # 权限检查：确保当前用户是该班级的教师
    is_teacher = db.exec(
        select(ClassMember).where(
            ClassMember.class_id == course_in.class_id,
            ClassMember.user_id == current_user.id,
            ClassMember.role == "teacher",
        )
    ).first()
    if not is_teacher and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="必须是班级教师才能创建课程",
        )
    
    # 创建课程
    course = Course(
        **course_in.dict(),
        teacher_id=current_user.id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    
    return course


@router.get("/", response_model=List[CourseRead])
def read_courses(
    skip: int = 0,
    limit: int = 100,
    class_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取课程列表
    """
    query = select(Course)
    
    # 过滤条件
    if class_id:
        query = query.where(Course.class_id == class_id)
    
    # 如果不是管理员，只能查看自己所在班级的课程
    if current_user.role != "admin":
        # 获取用户所在的班级
        class_members = db.exec(
            select(ClassMember).where(ClassMember.user_id == current_user.id)
        ).all()
        class_ids = [cm.class_id for cm in class_members]
        
        # 如果没有指定班级ID，则查询所有所在班级的课程
        if not class_id:
            query = query.where(Course.class_id.in_(class_ids))
        # 如果指定了班级ID，则检查用户是否是该班级的成员
        elif class_id not in class_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此班级的课程",
            )
    
    # 执行查询
    courses = db.exec(query.offset(skip).limit(limit)).all()
    return courses


@router.get("/{course_id}", response_model=CourseRead)
def read_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取课程详情
    """
    # 查询课程
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在",
        )
    
    # 权限检查：管理员可以查看所有课程，其他人只能查看自己所在班级的课程
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
                detail="无权查看此课程",
            )
    
    return course


@router.put("/{course_id}", response_model=CourseRead)
def update_course(
    course_id: int,
    course_in: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新课程信息
    """
    # 查询课程
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在",
        )
    
    # 权限检查：只有课程教师和管理员可以更新课程
    if current_user.role != "admin" and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新此课程",
        )
    
    # 更新课程信息
    course_data = course_in.dict(exclude_unset=True)
    for key, value in course_data.items():
        setattr(course, key, value)
    
    db.add(course)
    db.commit()
    db.refresh(course)
    
    return course


@router.delete("/{course_id}", response_model=dict)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    删除课程
    """
    # 查询课程
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在",
        )
    
    # 权限检查：只有课程教师和管理员可以删除课程
    if current_user.role != "admin" and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此课程",
        )
    
    # 删除课程
    db.delete(course)
    db.commit()
    
    return {"message": "课程已删除"}


@router.get("/class/{class_id}", response_model=List[CourseRead])
def read_class_courses(
    class_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取班级的课程列表
    """
    # 查询班级
    class_ = db.get(Class, class_id)
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在",
        )
    
    # 权限检查：只有班级成员可以查看班级课程
    if current_user.role != "admin":
        is_member = db.exec(
            select(ClassMember).where(
                ClassMember.class_id == class_id,
                ClassMember.user_id == current_user.id,
            )
        ).first()
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此班级课程",
            )
    
    # 获取班级课程列表
    courses = db.exec(
        select(Course)
        .where(Course.class_id == class_id)
        .offset(skip)
        .limit(limit)
    ).all()
    
    return courses 