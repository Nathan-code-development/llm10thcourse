from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_active_user, get_current_admin_user, get_db
from app.core.security import get_password_hash
from app.models.user import User, UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[UserRead])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    获取用户列表(仅管理员)
    """
    users = db.exec(select(User).offset(skip).limit(limit)).all()
    return users


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取当前登录用户信息
    """
    return current_user


@router.put("/me", response_model=UserRead)
def update_current_user(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新当前登录用户信息
    """
    # 如果要更新用户名，检查是否已经存在
    if user_in.username and user_in.username != current_user.username:
        user = db.exec(select(User).where(User.username == user_in.username)).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在",
            )
    
    # 如果要更新邮箱，检查是否已经存在
    if user_in.email and user_in.email != current_user.email:
        user = db.exec(select(User).where(User.email == user_in.email)).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在",
            )
    
    # 更新用户信息
    user_data = user_in.dict(exclude_unset=True)
    if user_in.password:
        user_data["hashed_password"] = get_password_hash(user_in.password)
        del user_data["password"]
    
    for key, value in user_data.items():
        setattr(current_user, key, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取指定用户信息
    """
    # 非管理员只能查看自己的信息
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此用户信息",
        )
    
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    更新指定用户信息(仅管理员)
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    # 如果要更新用户名，检查是否已经存在
    if user_in.username and user_in.username != user.username:
        existing_user = db.exec(
            select(User).where(User.username == user_in.username)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在",
            )
    
    # 如果要更新邮箱，检查是否已经存在
    if user_in.email and user_in.email != user.email:
        existing_user = db.exec(
            select(User).where(User.email == user_in.email)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在",
            )
    
    # 更新用户信息
    user_data = user_in.dict(exclude_unset=True)
    if user_in.password:
        user_data["hashed_password"] = get_password_hash(user_in.password)
        del user_data["password"]
    
    for key, value in user_data.items():
        setattr(user, key, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}", response_model=dict)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    删除用户(仅管理员)
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    # 阻止删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号",
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "用户已删除"} 