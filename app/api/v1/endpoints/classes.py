from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_active_user, get_current_admin_user, get_db
from app.models.class_model import Class, ClassCreate, ClassMember, ClassMemberCreate, ClassMemberRead, ClassRead, ClassUpdate
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.services.notification_service import create_notification

router = APIRouter()


@router.post("/", response_model=ClassRead)
def create_class(
    class_in: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    创建班级
    """
    # 创建班级
    class_ = Class(
        **class_in.dict(),
        created_by=current_user.id,
    )
    db.add(class_)
    db.commit()
    db.refresh(class_)
    
    # 将创建者添加为班级成员(教师角色)
    class_member = ClassMember(
        class_id=class_.id,
        user_id=current_user.id,
        role="teacher",
    )
    db.add(class_member)
    db.commit()
    
    return class_


@router.get("/", response_model=List[ClassRead])
def read_classes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取班级列表
    """
    # 如果是管理员，获取所有班级
    if current_user.role == "admin":
        classes = db.exec(select(Class).offset(skip).limit(limit)).all()
    else:
        # 获取用户所在的班级
        class_members = db.exec(
            select(ClassMember).where(ClassMember.user_id == current_user.id)
        ).all()
        class_ids = [cm.class_id for cm in class_members]
        classes = db.exec(
            select(Class).where(Class.id.in_(class_ids)).offset(skip).limit(limit)
        ).all()
    
    return classes


@router.get("/{class_id}", response_model=ClassRead)
def read_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取班级详情
    """
    # 查询班级
    class_ = db.get(Class, class_id)
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在",
        )
    
    # 权限检查：管理员可以查看所有班级，其他人只能查看自己所在的班级
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
                detail="无权查看此班级",
            )
    
    return class_


@router.put("/{class_id}", response_model=ClassRead)
def update_class(
    class_id: int,
    class_in: ClassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新班级信息
    """
    # 查询班级
    class_ = db.get(Class, class_id)
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在",
        )
    
    # 权限检查：只有班级创建者和管理员可以更新班级信息
    if current_user.role != "admin" and class_.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新此班级",
        )
    
    # 更新班级信息
    class_data = class_in.dict(exclude_unset=True)
    for key, value in class_data.items():
        setattr(class_, key, value)
    
    db.add(class_)
    db.commit()
    db.refresh(class_)
    
    return class_


@router.delete("/{class_id}", response_model=dict)
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    删除班级(仅管理员)
    """
    # 查询班级
    class_ = db.get(Class, class_id)
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在",
        )
    
    # 删除班级成员
    members = db.exec(
        select(ClassMember).where(ClassMember.class_id == class_id)
    ).all()
    for member in members:
        db.delete(member)
    
    # 删除班级
    db.delete(class_)
    db.commit()
    
    return {"message": "班级已删除"}


@router.post("/{class_id}/members", response_model=ClassMemberRead)
def add_class_member(
    class_id: int,
    member_in: ClassMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    添加班级成员
    """
    # 查询班级
    class_ = db.get(Class, class_id)
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在",
        )
    
    # 权限检查：只有班级创建者、管理员和班级教师可以添加成员
    if current_user.role != "admin" and class_.created_by != current_user.id:
        is_teacher = db.exec(
            select(ClassMember).where(
                ClassMember.class_id == class_id,
                ClassMember.user_id == current_user.id,
                ClassMember.role == "teacher",
            )
        ).first()
        if not is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权添加班级成员",
            )
    
    # 检查用户是否存在
    user = db.get(User, member_in.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    # 检查用户是否已经是班级成员
    existing_member = db.exec(
        select(ClassMember).where(
            ClassMember.class_id == class_id,
            ClassMember.user_id == member_in.user_id,
        )
    ).first()
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已经是班级成员",
        )
    
    # 添加班级成员
    class_member = ClassMember(**member_in.dict())
    db.add(class_member)
    db.commit()
    db.refresh(class_member)
    
    # 发送通知给用户
    create_notification(
        db=db,
        user_id=member_in.user_id,
        title=f"您已被添加到班级: {class_.name}",
        content=f"您已被添加到班级: {class_.name}，角色为: {member_in.role}",
        notification_type=NotificationType.ASSIGNMENT,
    )
    
    return class_member


@router.get("/{class_id}/members", response_model=List[ClassMemberRead])
def read_class_members(
    class_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取班级成员列表
    """
    # 查询班级
    class_ = db.get(Class, class_id)
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在",
        )
    
    # 权限检查：只有班级成员可以查看班级成员列表
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
                detail="无权查看此班级成员列表",
            )
    
    # 获取班级成员列表
    members = db.exec(
        select(ClassMember)
        .where(ClassMember.class_id == class_id)
        .offset(skip)
        .limit(limit)
    ).all()
    
    return members


@router.delete("/{class_id}/members/{user_id}", response_model=dict)
def remove_class_member(
    class_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    移除班级成员
    """
    # 查询班级
    class_ = db.get(Class, class_id)
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在",
        )
    
    # 权限检查：只有班级创建者、管理员和班级教师可以移除成员
    if current_user.role != "admin" and class_.created_by != current_user.id:
        is_teacher = db.exec(
            select(ClassMember).where(
                ClassMember.class_id == class_id,
                ClassMember.user_id == current_user.id,
                ClassMember.role == "teacher",
            )
        ).first()
        if not is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权移除班级成员",
            )
    
    # 查询班级成员
    member = db.exec(
        select(ClassMember).where(
            ClassMember.class_id == class_id,
            ClassMember.user_id == user_id,
        )
    ).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级成员不存在",
        )
    
    # 防止移除班级创建者
    if user_id == class_.created_by:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能移除班级创建者",
        )
    
    # 移除班级成员
    db.delete(member)
    db.commit()
    
    return {"message": "班级成员已移除"}


@router.post("/{class_id}/invite", response_model=dict)
def invite_to_class(
    class_id: int,
    user_email: str,
    role: str = "student",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    邀请用户加入班级
    """
    # 查询班级
    class_ = db.get(Class, class_id)
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在",
        )
    
    # 权限检查：只有班级创建者、管理员和班级教师可以邀请成员
    if current_user.role != "admin" and class_.created_by != current_user.id:
        is_teacher = db.exec(
            select(ClassMember).where(
                ClassMember.class_id == class_id,
                ClassMember.user_id == current_user.id,
                ClassMember.role == "teacher",
            )
        ).first()
        if not is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权邀请用户加入班级",
            )
    
    # 检查角色是否有效
    if role not in ["teacher", "student"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的角色，必须是 'teacher' 或 'student'",
        )
    
    # 查找用户
    user = db.exec(
        select(User).where(User.email == user_email)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该邮箱对应的用户",
        )
    
    # 检查用户是否已经是班级成员
    existing_member = db.exec(
        select(ClassMember).where(
            ClassMember.class_id == class_id,
            ClassMember.user_id == user.id,
        )
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已经是班级成员",
        )
    
    # 创建班级成员
    class_member = ClassMember(
        class_id=class_id,
        user_id=user.id,
        role=role,
    )
    db.add(class_member)
    db.commit()
    
    # 发送通知给用户
    create_notification(
        db=db,
        user_id=user.id,
        title=f"您已被邀请加入班级: {class_.name}",
        content=f"您已被{current_user.username}邀请加入班级: {class_.name}，角色为: {role}",
        notification_type=NotificationType.ASSIGNMENT,
    )
    
    return {
        "message": f"已成功邀请用户加入班级",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": role,
    } 